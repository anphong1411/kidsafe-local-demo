"""Authenticated loopback IPC; a tray lease expires five seconds after icon loss.

This token-based prototype is NOT an anti-spoofing proof against another process
running as the same user. The installed ACL/PID/session checks require lab review.
"""
from __future__ import annotations

import hmac
import json
import threading
from agent.storage import QueueFull
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class TrayIPC:
    def __init__(self, token, status, lease, request_time, *, port=17843, verify_peer=None):
        if len(token) < 32:
            raise ValueError("IPC token needs at least 32 characters")
        verify_peer = verify_peer or (lambda payload, address: False)
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass
            def _handle(self):
                if self.client_address[0] != "127.0.0.1" or not hmac.compare_digest(self.headers.get("Authorization", ""), "Bearer " + token):
                    self.send_error(403)
                    return
                if self.headers.get("Origin"):
                    self.send_error(403)
                    return
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 <= size <= 4096:
                    self.send_error(413)
                    return
                payload = json.loads(self.rfile.read(size) or b"{}")
                if not isinstance(payload, dict):
                    raise ValueError('Expected an IPC object')
                if not verify_peer(payload, self.client_address):
                    self.send_error(403)
                    return
                if self.command == "POST" and self.path == "/lease":
                    if payload.get("icon_visible") is not True:
                        self.send_error(403)
                        return
                    lease(payload)
                    result = status()
                elif self.command == "POST" and self.path == "/request-time":
                    minutes = payload.get('minutes', 15)
                    if type(minutes) is not int or minutes not in (5, 10, 15):
                        self.send_error(400)
                        return
                    result = request_time(minutes)
                elif self.command == "GET" and self.path == "/status":
                    result = status()
                else:
                    self.send_error(404)
                    return
                data = json.dumps(result).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            def do_GET(self):
                try:
                    self._handle()
                except (ValueError, TypeError):
                    self.send_error(400)
                except QueueFull:
                    self.send_error(503)
            do_POST = do_GET
        self.server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        self.server.daemon_threads = True
        self.thread = None
    def start(self):
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        if self.thread:
            self.thread.join(2)
