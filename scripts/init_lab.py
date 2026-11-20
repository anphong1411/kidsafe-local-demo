"""Initialize private local lab configuration without changing Windows trust/DNS."""
from __future__ import annotations

import argparse
import base64
import json
import os
import secrets
import subprocess
from pathlib import Path

from scripts.create_lab_tls import generate


def initialize(root: Path, hosts: list[str]) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    env_path = root / 'lab.json'
    if env_path.exists():
        raise ValueError('Lab already initialized; refusing to replace credentials')
    # Restrict the runtime directory before creating any secret on Windows.
    if os.name == 'nt':
        account = subprocess.check_output(['whoami', '/user', '/fo', 'csv', '/nh'], text=True)
        import csv
        sid = next(csv.reader([account.strip()]))[1]
        subprocess.run(['icacls', str(root.resolve()), '/inheritance:r', '/grant:r',
                        f'*{sid}:(OI)(CI)F', '*S-1-5-18:(OI)(CI)F',
                        '*S-1-5-32-544:(OI)(CI)F'], check=True, capture_output=True)
    pin = generate(root / 'tls', hosts)
    config = {
        'KIDSAFE_DATABASE_URL': 'sqlite:///' + (root.resolve() / 'kidsafe.db').as_posix(),
        'KIDSAFE_ENCRYPTION_KEY': base64.b64encode(secrets.token_bytes(32)).decode(),
        'KIDSAFE_SIGNING_SEED': base64.b64encode(secrets.token_bytes(32)).decode(),
        'KIDSAFE_ALLOWED_HOSTS': ','.join(dict.fromkeys(['localhost', '127.0.0.1', *hosts])),
        'demo_username': 'parent@kidsafe.local',
        'demo_password': secrets.token_urlsafe(18),
        'certificate_pin_sha256': pin,
    }
    env_path.write_text(json.dumps(config, indent=2), encoding='utf-8')
    return env_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.runtime'))
    parser.add_argument('--host', action='append', default=[])
    args = parser.parse_args()
    print('Private configuration created:', initialize(args.root, args.host))
    print('No OS trust store, DNS, firewall, or service configuration changed.')
