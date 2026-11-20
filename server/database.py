from contextlib import contextmanager
from pathlib import Path
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from .models import Base


class Database:
    def __init__(self, url: str):
        if url.startswith("sqlite:///") and ":memory:" not in url:
            Path(url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(url, connect_args={"check_same_thread": False, "timeout": 15})
        @event.listens_for(self.engine, "connect")
        def configure(connection, _):
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("PRAGMA busy_timeout=15000")
        self.factory = sessionmaker(self.engine, expire_on_commit=False)

    def migrate(self):
        Base.metadata.create_all(self.engine)
        with self.engine.begin() as db:
            db.execute(text("""CREATE TABLE IF NOT EXISTS events (
                ts TEXT NOT NULL, device_id TEXT NOT NULL, child_id TEXT NOT NULL,
                type TEXT NOT NULL, subject TEXT NOT NULL, duration_sec INTEGER NOT NULL,
                policy_id TEXT NOT NULL)"""))
            db.execute(text("CREATE INDEX IF NOT EXISTS event_child_ts ON events(child_id, ts)"))
            db.execute(text("CREATE TABLE IF NOT EXISTS schema_versions (version INTEGER PRIMARY KEY, applied_at TEXT DEFAULT CURRENT_TIMESTAMP)"))
            db.execute(text("INSERT OR IGNORE INTO schema_versions(version) VALUES (1)"))
            # Additive migrations preserve accounts and data from earlier lab builds.
            additions = {"accounts": {"display_name_enc": "TEXT NOT NULL DEFAULT ''"},
                         "devices": {"allocation_effective_date": "TEXT NOT NULL DEFAULT ''",
                                      "previous_weekday_sec": "INTEGER NOT NULL DEFAULT 0",
                                      "previous_weekend_sec": "INTEGER NOT NULL DEFAULT 0",
                                      "reported_policy_version": "INTEGER NOT NULL DEFAULT 0",
                                      "status": "TEXT NOT NULL DEFAULT 'unknown'"},
                         "transfers": {"effective_date": "TEXT NOT NULL DEFAULT ''"}}
            for table, columns in additions.items():
                present = {row[1] for row in db.execute(text(f"PRAGMA table_info({table})"))}
                for name, declaration in columns.items():
                    if name not in present:
                        db.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {declaration}"))
            db.execute(text("INSERT OR IGNORE INTO schema_versions(version) VALUES (2)"))
            db.execute(text("INSERT OR IGNORE INTO schema_versions(version) VALUES (3)"))

    @contextmanager
    def session(self):
        with self.factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise
