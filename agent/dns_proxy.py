"""Loopback UDP/TCP DNS proxy. Construction and tests never change adapter DNS."""
from __future__ import annotations

import socket
import socketserver
import struct
import threading
import time
from collections import OrderedDict

import tldextract
from dnslib import CNAME, DNSHeader, DNSRecord, QTYPE, RCODE, RR

_extract = tldextract.TLDExtract(suffix_list_urls=(), cache_dir=None, include_psl_private_domains=False)


def normalize_domain(value, *, allow_underscore=False):
    value = str(value).rstrip(".").lower()
    if not value or len(value) > 253 or any(c in value for c in "/\\?#:@"):
        raise ValueError("Invalid domain")
    value = value.encode("idna").decode("ascii")
    labels = value.split(".")
    permitted = '-_' if allow_underscore else '-'
    if any(not label or len(label) > 63 or label.startswith("-") or label.endswith("-") or not all(c.isalnum() or c in permitted for c in label) for label in labels):
        raise ValueError("Invalid DNS label")
    return value


def event_domain(value):
    value = normalize_domain(value, allow_underscore=True)
    result = _extract(value)
    # Private/single-label names are not public registrable domains; do not log
    # host/user identifiers disguised as local DNS service-discovery names.
    return result.top_domain_under_public_suffix or ''


def matches(domain, rule):
    domain, rule = normalize_domain(domain, allow_underscore=True), normalize_domain(rule)
    return domain == rule or domain.endswith("." + rule)


SAFESEARCH = {"www.google.com": "forcesafesearch.google.com", "google.com": "forcesafesearch.google.com", "www.google.com.vn": "forcesafesearch.google.com", "google.com.vn": "forcesafesearch.google.com", "www.bing.com": "strict.bing.com", "bing.com": "strict.bing.com", "www.youtube.com": "restrict.youtube.com", "youtube.com": "restrict.youtube.com", "m.youtube.com": "restrict.youtube.com", "youtubei.googleapis.com": "restrict.youtube.com"}
DOH_ENDPOINTS = frozenset({"dns.google", "cloudflare-dns.com", "mozilla.cloudflare-dns.com", "dns.quad9.net", "dns.nextdns.io", "doh.opendns.com", "use-application-dns.net"})


class Resolver:
    def __init__(self, blocked_domains=(), upstream=("1.1.1.1", 53), *, safesearch=True, block_doh=False, timeout=2, on_query=None, upstream_query=None, cache_size=2048):
        if upstream[0] in ("127.0.0.1", "::1") and upstream[1] == 53:
            raise ValueError("Upstream cannot loop back to local port 53")
        self.blocked = frozenset(normalize_domain(d) for d in blocked_domains)
        self.upstream = upstream
        self.safesearch, self.block_doh, self.timeout = safesearch, block_doh, timeout
        self.on_query = on_query or (lambda domain, blocked: None)
        self.upstream_query = upstream_query or self.forward
        self.cache, self.cache_size = OrderedDict(), cache_size
        self.lock = threading.Lock()

    @staticmethod
    def _read_exact(sock, amount):
        output = b""
        while len(output) < amount:
            part = sock.recv(amount - len(output))
            if not part:
                raise ConnectionError("Truncated DNS frame")
            output += part
        return output

    def forward(self, data, tcp=False):
        family = socket.AF_INET6 if ":" in self.upstream[0] else socket.AF_INET
        with socket.socket(family, socket.SOCK_STREAM if tcp else socket.SOCK_DGRAM) as sock:
            sock.settimeout(self.timeout)
            sock.connect(self.upstream)
            if tcp:
                sock.sendall(struct.pack("!H", len(data)) + data)
                length = struct.unpack("!H", self._read_exact(sock, 2))[0]
                if length > 16384:
                    raise ValueError("Oversized upstream response")
                answer = self._read_exact(sock, length)
            else:
                sock.send(data)
                answer = sock.recv(16384)
        query, response = DNSRecord.parse(data), DNSRecord.parse(answer)
        if response.header.id != query.header.id or response.header.qr != 1 or response.questions != query.questions:
            raise ValueError("Mismatched upstream response")
        if response.header.tc and not tcp:
            return self.forward(data, tcp=True)
        return answer

    def resolve(self, data, tcp=False):
        query = DNSRecord.parse(data)
        if len(query.questions) != 1 or query.header.qr or query.header.opcode:
            return DNSRecord(DNSHeader(id=query.header.id, qr=1, rcode=RCODE.FORMERR)).pack()
        if str(query.q.qname) == '.':
            try:
                return self.upstream_query(data, tcp)
            except (OSError, ValueError, ConnectionError):
                error = query.reply()
                error.header.rcode = RCODE.SERVFAIL
                return error.pack()
        name = normalize_domain(query.q.qname, allow_underscore=True)
        reply = query.reply()
        reply.header.ra = 1
        blocked = any(matches(name, rule) for rule in self.blocked) or self.block_doh and any(matches(name, rule) for rule in DOH_ENDPOINTS)
        subject = event_domain(name)
        if subject:
            self.on_query(subject, bool(blocked))
        if blocked:
            reply.header.rcode = RCODE.NXDOMAIN
            return reply.pack()
        if self.safesearch and name in SAFESEARCH and query.q.qtype in (64, 65):
            # Endpoint hints must not bypass the restricted CNAME on A/AAAA.
            return reply.pack()
        key = (name, query.q.qtype, query.q.qclass, tcp)
        now = time.monotonic()
        with self.lock:
            cached = self.cache.get(key)
            if cached and cached[0] > now:
                result = DNSRecord.parse(cached[2])
                result.header.id = query.header.id
                for rr in (*result.rr, *result.auth, *result.ar):
                    rr.ttl = max(0, rr.ttl - int(now - cached[1]))
                self.cache.move_to_end(key)
                return result.pack()
            self.cache.pop(key, None)
        try:
            target = SAFESEARCH.get(name) if self.safesearch else None
            if target and query.q.qtype in (QTYPE.A, QTYPE.AAAA, QTYPE.CNAME):
                answer = DNSRecord.parse(self.upstream_query(DNSRecord.question(target, QTYPE[query.q.qtype]).pack(), tcp))
                reply.header.rcode = answer.header.rcode
                if answer.header.rcode == RCODE.NOERROR:
                    reply.add_answer(RR(name, QTYPE.CNAME, ttl=60, rdata=CNAME(target)))
                    for rr in answer.rr:
                        reply.add_answer(rr)
                result = reply
            else:
                result = DNSRecord.parse(self.upstream_query(data, tcp))
                if result.header.id != query.header.id or result.questions != query.questions:
                    raise ValueError("Mismatched upstream response")
            ttl = min([300] + [rr.ttl for rr in (*result.rr, *result.auth)]) if result.rr or result.auth else 0
            if ttl > 0:
                with self.lock:
                    self.cache[key] = (now + ttl, now, result.pack())
                    while len(self.cache) > self.cache_size:
                        self.cache.popitem(last=False)
            return result.pack()
        except (OSError, ValueError, ConnectionError):
            reply.header.rcode = RCODE.SERVFAIL
            return reply.pack()


class _BoundedServer:
    daemon_threads = True
    allow_reuse_address = True

    def process_request(self, request, client_address):
        if not self.slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except BaseException:
            self.slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.slots.release()


class _UDP(_BoundedServer, socketserver.ThreadingUDPServer):
    pass


class _TCP(_BoundedServer, socketserver.ThreadingTCPServer):
    pass


class _UDP6(_UDP):
    address_family = socket.AF_INET6


class _TCP6(_TCP):
    address_family = socket.AF_INET6


class DNSProxy:
    def __init__(self, resolver, host="127.0.0.1", port=53):
        if host not in ("127.0.0.1", "::1"):
            raise ValueError("DNS proxy must bind loopback")
        class UDPHandler(socketserver.BaseRequestHandler):
            def handle(inner):
                data, sock = inner.request
                if len(data) > 4096:
                    return
                try:
                    sock.sendto(resolver.resolve(data), inner.client_address)
                except Exception:
                    # Malformed packets must not kill the resolver worker.
                    return
        class TCPHandler(socketserver.BaseRequestHandler):
            def handle(inner):
                inner.request.settimeout(3)
                try:
                    size = struct.unpack("!H", Resolver._read_exact(inner.request, 2))[0]
                    if not 12 <= size <= 4096:
                        return
                    data = Resolver._read_exact(inner.request, size)
                    answer = resolver.resolve(data, True)
                    inner.request.sendall(struct.pack("!H", len(answer)) + answer)
                except Exception:
                    return
        udp_class, tcp_class = (_UDP6, _TCP6) if host == "::1" else (_UDP, _TCP)
        self.udp = udp_class((host, port), UDPHandler)
        try:
            self.tcp = tcp_class((host, self.udp.server_address[1]), TCPHandler)
        except BaseException:
            self.udp.server_close()
            raise
        self.udp.slots, self.tcp.slots = threading.BoundedSemaphore(32), threading.BoundedSemaphore(32)
        self.port = self.udp.server_address[1]
        self.threads = []

    def start(self):
        for server in (self.udp, self.tcp):
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            self.threads.append(thread)
        return self

    def stop(self):
        for server in (self.udp, self.tcp):
            server.shutdown()
            server.server_close()
        for thread in self.threads:
            thread.join(2)
