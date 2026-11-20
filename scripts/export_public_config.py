"""Export only CA/pins/signing public key for enrollment on a child lab machine."""
import json
import argparse
from pathlib import Path
import shutil

from scripts.run_server import load_config
from server.config import Settings
from server.security import Crypto


def export(path: Path):
    config = load_config(path)
    settings = Settings.from_env()
    crypto = Crypto(settings.encryption_key, settings.signing_seed)
    destination = path.parent / 'public'
    destination.mkdir(exist_ok=True)
    shutil.copyfile(path.parent / 'tls' / 'ca.crt', destination / 'ca.crt')
    value = {'certificate_pin': config['certificate_pin_sha256'],
             'signing_public_key': crypto.envelope({})['public_key']}
    (destination / 'server-public.json').write_text(json.dumps(value, indent=2), encoding='utf-8')
    print(f'Public CA and enrollment settings exported to {destination} (no passwords or private keys).')
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path('.runtime/lab.json'))
    export(parser.parse_args().config)


if __name__ == '__main__':
    main()
