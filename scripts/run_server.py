"""Run KidSafe on loopback TLS by default; use --host for a configured LAN lab."""
import argparse
import json
import os
import ssl
from pathlib import Path

import uvicorn


def load_config(path: Path) -> dict:
    config = json.loads(path.read_text(encoding='utf-8'))
    for name, value in config.items():
        if name.startswith('KIDSAFE_'):
            os.environ[name] = value
    return config


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path('.runtime/lab.json'))
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8443)
    args = parser.parse_args()
    load_config(args.config)
    from server.config import Settings
    from server.app import create_app
    tls = args.config.parent / 'tls'
    app = create_app(Settings.from_env())
    app.state.pairing_tls = (tls / 'ca.crt', tls / 'server.crt', args.port)
    # Uvicorn chooses its own loop factory. On Windows, Selector avoids noisy
    # Proactor pipe cleanup tracebacks when a browser resets a TLS connection.
    loop = 'asyncio:SelectorEventLoop' if os.name == 'nt' else 'auto'
    uvicorn.run(app, host=args.host, port=args.port,
                loop=loop,
                ssl_keyfile=str(tls / 'server.key'), ssl_certfile=str(tls / 'server.crt'),
                ssl_version=ssl.PROTOCOL_TLS_SERVER,
                ssl_ciphers='ECDHE+AESGCM:ECDHE+CHACHA20', access_log=False)
