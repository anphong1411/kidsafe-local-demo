"""TLS CA validation plus certificate pinning before any bearer token is sent."""
from __future__ import annotations

import hashlib
import http.client
import json
import ssl
from urllib.parse import urlsplit


class PinnedHTTPS:
    def __init__(self, base_url, ca_file, certificate_sha256, timeout=10):
        url = urlsplit(base_url)
        if url.scheme != "https" or not url.hostname or url.username or url.password or url.query or url.fragment or url.path not in ("", "/"):
            raise ValueError("Expected HTTPS server origin")
        pin = certificate_sha256.lower().replace(":", "")
        if len(pin) != 64 or any(c not in "0123456789abcdef" for c in pin):
            raise ValueError("Invalid SHA-256 certificate pin")
        self.host, self.port, self.pin, self.timeout = url.hostname, url.port or 443, pin, timeout
        self.context = ssl.create_default_context(cafile=str(ca_file))
        self.context.minimum_version = ssl.TLSVersion.TLSv1_2

    def request(self, method, path, body=None, token=None, headers=None):
        if not (path.startswith("/api/") or (method == "GET" and path == "/health" and not token)) or "\r" in path or "\n" in path:
            raise ValueError("Invalid API path")
        connection = http.client.HTTPSConnection(self.host, self.port, context=self.context, timeout=self.timeout)
        try:
            connection.connect()
            actual = hashlib.sha256(connection.sock.getpeercert(binary_form=True)).hexdigest()
            if actual != self.pin:
                raise ssl.SSLError("Server certificate pin mismatch")
            outgoing = {"Content-Type": "application/json", **(headers or {})}
            if token:
                outgoing["Authorization"] = "Bearer " + token
            connection.request(method, path, json.dumps(body, separators=(",", ":")) if body is not None else None, outgoing)
            response = connection.getresponse()
            raw = response.read(2 * 1024 * 1024 + 1)
            if len(raw) > 2 * 1024 * 1024:
                raise ValueError("Oversized API response")
            if response.status >= 400:
                raise HTTPFailure(response.status)
            return json.loads(raw) if raw else {}
        finally:
            connection.close()


class HTTPFailure(RuntimeError):
    def __init__(self, status):
        super().__init__(f"API returned HTTP {status}")
        self.status = status
