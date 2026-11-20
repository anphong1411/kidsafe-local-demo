"""Device protocol client. It never modifies Windows adapters, services, or sessions."""
from __future__ import annotations

import base64
import hashlib
import json
import queue
import socket
import ssl
import threading
import time
from datetime import datetime

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from agent.policy import canonical, install_policy
from agent.transport import HTTPFailure


def verify_command(envelope, public_key):
    payload = envelope["payload"]
    Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key, validate=True)).verify(base64.b64decode(envelope["signature"], validate=True), canonical(payload))
    return payload


class DeviceSync:
    def __init__(self, store, transport, credentials, public_key):
        self.store, self.transport, self.credentials, self.public_key = store, transport, credentials, public_key
        self.incoming = queue.Queue(maxsize=1000)
        self.stop_event = threading.Event()
        self.token_lock = threading.RLock()

    def enroll(self, code, fingerprint, name):
        response = self.transport.request("POST", "/api/device/enroll", {"code": code, "fingerprint": fingerprint, "name": name})
        if response["signing_public_key"] != self.public_key:
            raise ValueError("Enrollment key differs from preconfigured signing key")
        install_policy(self.store, response["policy"], self.public_key, response["device_id"])
        self.credentials.update({key: response[key] for key in ("device_id", "child_id", "access_token", "refresh_token")})
        return response

    def call(self, method, path, body=None, headers=None):
        with self.token_lock:
            token = self.credentials["access_token"]
        try:
            return self.transport.request(method, path, body, token, headers)
        except HTTPFailure as error:
            if error.status != 401:
                raise
        with self.token_lock:
            response = self.transport.request("POST", "/api/device/refresh", {"device_id": self.credentials["device_id"], "refresh_token": self.credentials["refresh_token"]})
            self.credentials.update({key: response[key] for key in ("access_token", "refresh_token")})
            self.persist_credentials()
            return self.transport.request(method, path, body, self.credentials["access_token"], headers)

    def persist_credentials(self):
        from agent.windows import protect_secret
        encrypted = protect_secret(json.dumps(self.credentials).encode())
        self.store.put("credentials_dpapi", base64.b64encode(encrypted).decode())

    def heartbeat(self, snapshot):
        response = self.call("POST", "/api/device/heartbeat", snapshot)
        if not response.get("deletion_pending") and response.get("policy_version") != snapshot["policy_version"]:
            envelope = self.call("GET", "/api/device/policy")
            install_policy(self.store, envelope, self.public_key, self.credentials["device_id"])
            self.incoming.put(("policy", envelope["payload"]), timeout=2)
        if response.get("server_time"):
            self.incoming.put(("time", datetime.fromisoformat(response["server_time"].replace("Z", "+00:00")).timestamp()), timeout=2)
        peer_seconds = response.get("entertainment_other_sec")
        if not response.get("deletion_pending") and type(peer_seconds) is int and peer_seconds >= 0:
            groups = response.get("group_other_sec", {})
            groups = {key: value for key, value in groups.items() if type(value) is int and value >= 0} if isinstance(groups, dict) else {}
            self.incoming.put(("entertainment_usage", (snapshot["usage_date"], peer_seconds, groups)), timeout=2)
        for envelope in response.get("commands", []):
            self.incoming.put(("command", verify_command(envelope, self.public_key)), timeout=2)
        # ACK retries are durable and happen before further collection uploads.
        for command_id in self.store.get("pending_acks", []):
            self.call("POST", f"/api/device/commands/{command_id}/ack", {})
            with self.store.transaction() as db:
                self.store.write(db, "pending_acks", [value for value in self.store.get("pending_acks", []) if value != command_id])
        batch = None if response.get("deletion_pending") else self.store.batch()
        if batch:
            self.call("POST", "/api/device/events", {"events": batch[1]}, {"Idempotency-Key": batch[0]})
            self.store.acknowledge_batch(batch[0])
        return response

    def websocket(self):
        """Pin TLS before sending Authorization in the WebSocket handshake."""
        from websockets.sync.client import connect
        while not self.stop_event.is_set():
            tls = None
            try:
                raw = socket.create_connection((self.transport.host, self.transport.port), timeout=5)
                tls = self.transport.context.wrap_socket(raw, server_hostname=self.transport.host)
                if hashlib.sha256(tls.getpeercert(binary_form=True)).hexdigest() != self.transport.pin:
                    raise ssl.SSLError("WebSocket TLS certificate pin mismatch")
                host = self.transport.host
                host = f"[{host}]" if ":" in host else host
                # The socket is already encrypted and pinned. ws:// prevents the library
                # from wrapping TLS twice; no plaintext network socket is ever handed in.
                with connect(f"ws://{host}:{self.transport.port}/api/device/ws", sock=tls, proxy=None, additional_headers={"Authorization": "Bearer " + self.credentials["access_token"]}, open_timeout=5, max_size=1024 * 1024) as ws:
                    while not self.stop_event.is_set():
                        try:
                            message = json.loads(ws.recv(timeout=2))
                        except TimeoutError:
                            continue
                        if message.get("server_time"):
                            self.incoming.put(("time", datetime.fromisoformat(message["server_time"].replace("Z", "+00:00")).timestamp()), timeout=2)
                        for envelope in message.get("commands", []):
                            self.incoming.put(("command", verify_command(envelope, self.public_key)), timeout=2)
                        if "payload" in message:
                            self.incoming.put(("command", verify_command(message, self.public_key)), timeout=2)
            except Exception:
                self.stop_event.wait(2)
            finally:
                if tls:
                    tls.close()
