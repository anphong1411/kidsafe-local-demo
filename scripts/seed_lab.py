"""Create the local parent demo account idempotently without exposing its password."""
from pathlib import Path
import argparse
from uuid import uuid4

from sqlalchemy import select

from scripts.run_server import load_config
from server.app import create_app
from server.models import Account
from server.security import password_hash


def seed(path: Path):
    config = load_config(path)
    app = create_app()
    with app.state.database.session() as db:
        existing = db.scalar(select(Account).where(Account.username == config['demo_username']))
        if not existing:
            db.add(Account(id=str(uuid4()), username=config['demo_username'],
                           password=password_hash(config['demo_password']), role='parent'))
    app.state.database.engine.dispose()
    print(f'Local parent demo account ready. Credentials remain in {path}.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path('.runtime/lab.json'))
    seed(parser.parse_args().config)


if __name__ == '__main__':
    main()
