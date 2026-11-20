"""Explicit account creation; no embedded or default demo password."""
import argparse
from getpass import getpass
from pathlib import Path
from uuid import uuid4
from sqlalchemy import select
from .app import create_app
from .models import Account, Child
from .security import password_hash


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    parser.add_argument("--config", type=Path, help="Use the same lab.json as the running KidSafe server")
    parser.add_argument("--password", help="Omit to enter securely without shell history")
    parser.add_argument("--role", choices=["parent", "admin", "child-view"], default="parent")
    parser.add_argument("--child-id")
    args = parser.parse_args()
    if args.config is not None:
        from scripts.run_server import load_config
        load_config(args.config)
    password = args.password if args.password is not None else getpass("Password (at least 10 characters): ")
    app = create_app()
    with app.state.database.session() as db:
        if db.scalar(select(Account).where(Account.username == args.username)):
            parser.error("Username already exists")
        if args.role == "child-view" and (not args.child_id or not db.get(Child, args.child_id)):
            parser.error("child-view requires a valid --child-id")
        db.add(Account(id=str(uuid4()), username=args.username, password=password_hash(password), role=args.role, child_id=args.child_id))
    print(f"Created {args.role} account {args.username}")


if __name__ == "__main__":
    main()
