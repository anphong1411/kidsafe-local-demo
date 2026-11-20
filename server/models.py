"""SQLAlchemy schema v1. Event intentionally has exactly seven columns."""
from sqlalchemy import Boolean, Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    display_name_enc: Mapped[str] = mapped_column(Text, default="")
    password: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String, default="parent")
    child_id: Mapped[str | None] = mapped_column(String, nullable=True)
    failures: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[int] = mapped_column(Integer, default=0)


class Child(Base):
    __tablename__ = "children"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    parent_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"))
    name_enc: Mapped[str] = mapped_column(Text)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    policy: Mapped[str] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer, default=1)


class Session(Base):
    __tablename__ = "sessions"
    token_hash: Mapped[str] = mapped_column(String, primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"))
    csrf_hash: Mapped[str] = mapped_column(String)
    expires: Mapped[int] = mapped_column(Integer)


class Enrollment(Base):
    __tablename__ = "enrollments"
    code_hash: Mapped[str] = mapped_column(String, primary_key=True)
    child_id: Mapped[str] = mapped_column(ForeignKey("children.id"))
    expires: Mapped[int] = mapped_column(Integer)
    consent_at: Mapped[str] = mapped_column(String)
    consent_ip: Mapped[str] = mapped_column(String)


class Device(Base):
    __tablename__ = "devices"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    child_id: Mapped[str] = mapped_column(ForeignKey("children.id"))
    fingerprint_hash: Mapped[str] = mapped_column(String, unique=True)
    name_enc: Mapped[str] = mapped_column(Text)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_ack: Mapped[bool] = mapped_column(Boolean, default=False)
    weekday_sec: Mapped[int] = mapped_column(Integer, default=0)
    weekend_sec: Mapped[int] = mapped_column(Integer, default=0)
    allocation_effective_date: Mapped[str] = mapped_column(String, default="")
    previous_weekday_sec: Mapped[int] = mapped_column(Integer, default=0)
    previous_weekend_sec: Mapped[int] = mapped_column(Integer, default=0)
    sequence: Mapped[int] = mapped_column(Integer, default=0)
    last_seen: Mapped[int] = mapped_column(Integer, default=0)
    reported_policy_version: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String, default="unknown")
    usage: Mapped[str] = mapped_column(Text, default="{}")


class DeviceToken(Base):
    __tablename__ = "device_tokens"
    token_hash: Mapped[str] = mapped_column(String, primary_key=True)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id"))
    kind: Mapped[str] = mapped_column(String)
    expires: Mapped[int] = mapped_column(Integer)


# The seven-field event table is created with SQL in database.py. SQLite's
# implicit rowid preserves duplicate payloads; batch metadata provides idempotency.


class Batch(Base):
    __tablename__ = "batches"
    __table_args__ = (UniqueConstraint("device_id", "key"),)
    id: Mapped[str] = mapped_column(String, primary_key=True)
    device_id: Mapped[str] = mapped_column(String)
    key: Mapped[str] = mapped_column(String)
    body_hash: Mapped[str] = mapped_column(String)
    created: Mapped[int] = mapped_column(Integer)


class Command(Base):
    __tablename__ = "commands"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id"))
    child_id: Mapped[str] = mapped_column(String)
    key: Mapped[str] = mapped_column(String, unique=True)
    payload: Mapped[str] = mapped_column(Text)
    ack: Mapped[bool] = mapped_column(Boolean, default=False)
    created: Mapped[int] = mapped_column(Integer)


class Audit(Base):
    __tablename__ = "audit"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    child_id: Mapped[str | None] = mapped_column(String, nullable=True)
    actor: Mapped[str] = mapped_column(String)
    ts: Mapped[str] = mapped_column(String)
    ip: Mapped[str] = mapped_column(String)
    action: Mapped[str] = mapped_column(String)
    old: Mapped[str] = mapped_column(Text)
    new: Mapped[str] = mapped_column(Text)


class Transfer(Base):
    __tablename__ = "transfers"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    child_id: Mapped[str] = mapped_column(String)
    donor_id: Mapped[str] = mapped_column(String)
    recipient_id: Mapped[str | None] = mapped_column(String, nullable=True)
    weekday_sec: Mapped[int] = mapped_column(Integer)
    weekend_sec: Mapped[int] = mapped_column(Integer)
    effective_date: Mapped[str] = mapped_column(String)
    applied: Mapped[bool] = mapped_column(Boolean, default=False)
