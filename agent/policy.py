"""Ed25519 signed policies, canonical serialization and rollback protection."""
from __future__ import annotations

import base64
import json
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def canonical(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def verify_envelope(envelope, public_key_b64, device_id, previous_version=0):
    payload = envelope["payload"]
    Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key_b64, validate=True)).verify(base64.b64decode(envelope["signature"], validate=True), canonical(payload))
    if payload["device_id"] != device_id:
        raise ValueError("Policy is bound to another device")
    if not isinstance(payload["version"], int) or payload["version"] < previous_version:
        raise ValueError("Policy rollback rejected")
    schedule = payload["schedule"]
    if len(schedule) != 7 or any(len(day) != 48 or any(type(slot) is not bool for slot in day) for day in schedule):
        raise ValueError("Schedule must be 7 x 48 booleans")
    for day, seconds in payload.get("daily_grants", {}).items():
        datetime.strptime(day, "%Y-%m-%d")
        if not isinstance(seconds, (int, float)) or seconds < 0:
            raise ValueError("Invalid device allocation")
    allocation = payload.get("allocation", {})
    for key in ("weekday_sec", "weekend_sec"):
        if key not in allocation or type(allocation[key]) is not int or allocation[key] < 0:
            raise ValueError("Invalid recurring device allocation")
    return payload


def install_policy(store, envelope, public_key_b64, device_id):
    old = store.get("policy_envelope")
    previous = old["payload"]["version"] if old else 0
    policy = verify_envelope(envelope, public_key_b64, device_id, previous)
    if old and policy["version"] == previous and canonical(envelope["payload"]) != canonical(old["payload"]):
        raise ValueError("Same version contains different content")
    store.put("policy_envelope", envelope)
    return policy
