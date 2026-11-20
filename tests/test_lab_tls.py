import hashlib
import ssl
import socket
import threading

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import serialization

from scripts.create_lab_tls import generate


def test_tls_certificate_san_pin_and_chain(tmp_path):
    pin = generate(tmp_path, ['192.168.1.25'])
    cert = x509.load_pem_x509_certificate((tmp_path / 'server.crt').read_bytes())
    ca = x509.load_pem_x509_certificate((tmp_path / 'ca.crt').read_bytes())
    cert.verify_directly_issued_by(ca)
    assert pin == hashlib.sha256(cert.public_bytes(serialization.Encoding.DER)).hexdigest()
    san = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
    assert 'localhost' in san.get_values_for_type(x509.DNSName)
    assert '192.168.1.25' in [str(ip) for ip in san.get_values_for_type(x509.IPAddress)]
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.load_cert_chain(tmp_path / 'server.crt', tmp_path / 'server.key')


def test_tls_refuses_overwrite(tmp_path):
    (tmp_path / 'server.key').write_text('existing')
    with pytest.raises(ValueError, match='Refusing'):
        generate(tmp_path, [])
    assert (tmp_path / 'server.key').read_text() == 'existing'


def test_real_tls_loopback_rejects_untrusted_certificate(tmp_path):
    generate(tmp_path, [])
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(tmp_path / 'server.crt', tmp_path / 'server.key')
    listener = socket.socket()
    listener.bind(('127.0.0.1', 0))
    listener.listen(2)
    listener.settimeout(5)
    errors = []

    def serve():
        try:
            for _ in range(2):
                connection, _ = listener.accept()
                try:
                    with context.wrap_socket(connection, server_side=True) as tls:
                        tls.settimeout(5)
                        tls.sendall(tls.recv(4))
                except ssl.SSLError:
                    connection.close()  # expected untrusted client abort
        except Exception as exc:
            errors.append(exc)
        finally:
            listener.close()

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    address = listener.getsockname()
    trusted = ssl.create_default_context(cafile=str(tmp_path / 'ca.crt'))
    with socket.create_connection(address, timeout=5) as sock:
        with trusted.wrap_socket(sock, server_hostname='localhost') as tls:
            assert tls.version() in {'TLSv1.2', 'TLSv1.3'}
            tls.sendall(b'ping')
            assert tls.recv(4) == b'ping'
    with socket.create_connection(address, timeout=5) as sock:
        with pytest.raises(ssl.SSLCertVerificationError):
            ssl.create_default_context().wrap_socket(sock, server_hostname='localhost')
    thread.join(timeout=6)
    assert not thread.is_alive()
    assert not errors
