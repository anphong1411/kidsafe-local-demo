"""Read-only local TLS/auth smoke check, without printing credentials."""
import json
from pathlib import Path
import ssl

import httpx


def main():
    config = json.loads(Path('.runtime/lab.json').read_text(encoding='utf-8'))
    context = ssl.create_default_context(cafile='.runtime/tls/ca.crt')
    with httpx.Client(base_url='https://localhost:8443', verify=context, trust_env=False) as client:
        health = client.get('/health')
        health.raise_for_status()
        assert health.json()['product'] == 'KidSafe'
        login = client.post('/api/auth/login', json={'username': config['demo_username'], 'password': config['demo_password']})
        login.raise_for_status()
        client.headers['X-CSRF-Token'] = login.json()['csrf_token']
        client.get('/api/children').raise_for_status()
        client.post('/api/auth/logout').raise_for_status()
    print('PASS: real TLS server, CA verification, parent login, scoped read, logout')


if __name__ == '__main__':
    main()
