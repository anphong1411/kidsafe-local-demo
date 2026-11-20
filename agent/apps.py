"""Executable identity and process control; no process is touched on import."""
from __future__ import annotations

import hashlib
import os
import time
from pathlib import Path


class ExecutableHasher:
    def __init__(self):
        self.cache = {}

    def digest(self, filename):
        path = Path(filename).resolve(strict=True)
        before = path.stat()
        key = (str(path), before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns)
        if key in self.cache:
            return self.cache[key]
        hasher = hashlib.sha256()
        with path.open("rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                hasher.update(chunk)
        after = path.stat()
        if (before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise ValueError("Executable changed while hashing")
        if len(self.cache) >= 2048:
            self.cache.clear()
        self.cache[key] = hasher.hexdigest()
        return self.cache[key]


class AppRules:
    def __init__(self, mode, rules):
        if mode not in ("allowlist", "blocklist"):
            raise ValueError("Invalid application mode")
        self.mode = mode
        self.names = {rule["name"].casefold() for rule in rules if rule.get("name")}
        self.hashes = {rule["sha256"].lower() for rule in rules if rule.get("sha256")}
        if any(len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest) for digest in self.hashes):
            raise ValueError("Invalid SHA-256 application identity")
        if mode == "allowlist" and any(not r.get("sha256") for r in rules):
            raise ValueError("An allow rule needs an executable hash; names alone can be spoofed")

    def blocked(self, name, digest):
        if self.mode == "blocklist":
            return name.casefold() in self.names or digest.lower() in self.hashes
        return digest.lower() not in self.hashes


def terminate_verified(process, expected_path, expected_creation, hasher, rules, explain, *, extra_blocked=None):
    """Validate PID identity immediately before termination; caller limits scope to lab user."""
    path = process.exe()
    if Path(path).resolve() != Path(expected_path).resolve() or process.create_time() != expected_creation:
        return False
    name = process.name()
    digest = hasher.digest(path)
    if not rules.blocked(name, digest) and not (extra_blocked and extra_blocked(name, digest)):
        return False
    # Fail visible: explanation callback is mandatory before destructive action.
    explained = explain(name)
    if explained is None:
        return False
    if not explained:
        raise RuntimeError("Cannot show blocking explanation; stop enforcement")
    process.terminate()
    return True


class AppMonitor:
    """Only the configured child's processes; accounting follows the foreground app.

    Session 0 and a small set of protected Windows shell executables are never
    terminated. Hash rules continue to apply to renamed/copied app executables.
    Explanation acknowledgment is required before process termination.
    """
    SHELL_NAMES = frozenset({"explorer.exe", "dwm.exe", "sihost.exe", "ctfmon.exe", "taskhostw.exe", "fontdrvhost.exe", "runtimebroker.exe", "applicationframehost.exe", "shellexperiencehost.exe", "startmenuexperiencehost.exe", "searchhost.exe", "textinputhost.exe", "userinit.exe", "winlogon.exe"})

    def __init__(self, username, rules, emit, explain, *, processes=None, monotonic=time.monotonic,
                 on_usage=None, group_block=None, explain_group=None):
        import psutil
        self.username, self.rules, self.emit, self.explain = username.casefold(), rules, emit, explain
        self.processes = processes or (lambda: psutil.process_iter(["pid", "name", "username", "exe", "create_time"]))
        self.monotonic = monotonic
        self.on_usage = on_usage
        self.group_block = group_block
        self.explain_group = explain_group
        self.hasher = ExecutableHasher()
        self.foreground = None
        self.foreground_seconds = 0.0
        self.previous_tick = monotonic()
        self.remainders = {}

    def _shell(self, process, path):
        windows = Path(os.environ.get("SystemRoot", r"C:\Windows")).resolve()
        try:
            inside = Path(path).resolve().is_relative_to(windows)
        except (ValueError, OSError):
            inside = False
        return inside and process.name().casefold() in self.SHELL_NAMES

    def _close_foreground(self):
        if self.foreground:
            subject = self.foreground[2]
            total = self.foreground_seconds + self.remainders.get(subject, 0)
            self.emit("app_stop", subject, int(total))
            self.remainders[subject] = total - int(total)
            self.foreground = None
            self.foreground_seconds = 0.0

    def tick(self, foreground_pid, *, active, tray_pid=None, enforce=True):
        import psutil
        now = self.monotonic()
        elapsed = max(0, now - self.previous_tick)
        self.previous_tick = now
        if self.foreground and active and elapsed <= 5:
            self.foreground_seconds += elapsed
            if self.on_usage and enforce:
                self.on_usage(self.foreground[2], self.foreground[3], elapsed)
        if not enforce:
            self._close_foreground()
            return
        found = None
        explained_groups = set()
        for process in self.processes():
            try:
                if process.pid in (os.getpid(), tray_pid) or process.username().casefold() != self.username:
                    continue
                path, created, name = process.exe(), process.create_time(), process.name()
                if not path:
                    continue
                digest = None
                if not self._shell(process, path):
                    digest = self.hasher.digest(path)
                    group_notice = self.group_block(name, digest) if self.group_block else None
                    if group_notice or self.rules.blocked(name, digest):
                        def explain(subject):
                            if not group_notice:
                                return self.explain(subject)
                            if group_notice in explained_groups:
                                return True
                            acknowledged = self.explain_group(*group_notice)
                            if acknowledged:
                                explained_groups.add(group_notice)
                            return acknowledged

                        if terminate_verified(process, path, created, self.hasher, self.rules, explain,
                                              extra_blocked=self.group_block if group_notice else None):
                            self.emit("blocked_app", name, 0)
                        continue
                if process.pid == foreground_pid and active:
                    found = (process.pid, created, name, digest)
            except (psutil.NoSuchProcess, psutil.AccessDenied, FileNotFoundError, PermissionError):
                continue
        if found != self.foreground or not active or self.foreground_seconds >= 3600:
            self._close_foreground()
            if found and active:
                self.foreground = found
                self.emit("app_start", found[2], 0)

    def close(self):
        self._close_foreground()
