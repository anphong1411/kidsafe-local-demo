"""Create a local CA and server certificate; never install trust automatically."""
from __future__ import annotations

import argparse
import hashlib
import ipaddress
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID


def generate(destination: Path, hosts: list[str]) -> str:
    destination.mkdir(parents=True, exist_ok=True)
    names = ['ca.key', 'ca.crt', 'server.key', 'server.crt', 'server.sha256']
    if any((destination / name).exists() for name in names):
        raise ValueError('Refusing to replace existing TLS identity')
    now = datetime.now(timezone.utc)
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    ca_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'KidSafe local lab CA')])
    ca = (x509.CertificateBuilder().subject_name(ca_name).issuer_name(ca_name)
          .public_key(ca_key.public_key()).serial_number(x509.random_serial_number())
          .not_valid_before(now - timedelta(minutes=5)).not_valid_after(now + timedelta(days=365))
          .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
          .add_extension(x509.KeyUsage(False, False, False, False, False, True, True, False, False), critical=True)
          .sign(ca_key, hashes.SHA256()))
    key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    sans = []
    for host in dict.fromkeys(['localhost', '127.0.0.1', *hosts]):
        try:
            sans.append(x509.IPAddress(ipaddress.ip_address(host)))
        except ValueError:
            sans.append(x509.DNSName(host))
    cert = (x509.CertificateBuilder()
            .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'KidSafe lab server')]))
            .issuer_name(ca_name).public_key(key.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(minutes=5)).not_valid_after(now + timedelta(days=90))
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .add_extension(x509.SubjectAlternativeName(sans), critical=False)
            .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
            .sign(ca_key, hashes.SHA256()))
    for filename, private_key in [('ca.key', ca_key), ('server.key', key)]:
        (destination / filename).write_bytes(private_key.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption()))
    for filename, certificate in [('ca.crt', ca), ('server.crt', cert)]:
        (destination / filename).write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
    pin = hashlib.sha256(cert.public_bytes(serialization.Encoding.DER)).hexdigest()
    (destination / 'server.sha256').write_text(pin + '\n', encoding='ascii')
    return pin


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path('.runtime/tls'))
    parser.add_argument('--host', action='append', default=[])
    args = parser.parse_args()
    print('Server certificate SHA256:', generate(args.out, args.host))
