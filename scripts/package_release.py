"""Build a reproducible source archive without local data, secrets or dependencies."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile


SOURCE_DIRS = ("agent", "server", "dashboard", "tests", "scripts", "docs", "demo")
ROOT_FILES = ("README.md", "AGENTS.md", ".gitignore", "pyproject.toml", "requirements.txt", "requirements.in", "requirements.lock", "Start-KidSafe.ps1")
EXCLUDED_DIRS = {"__pycache__", ".pytest_cache", ".runtime", ".venv", ".git", ".tmp", ".local-tools", ".agents", "node_modules", "output", "outputs", "dist", "build", "releases"}
SECRET_SUFFIXES = {".db", ".sqlite", ".sqlite3", ".key", ".pem", ".pfx", ".p12", ".log", ".pyc", ".env"}


def source_files(root: Path):
    root = root.resolve()
    candidates = [root / name for name in ROOT_FILES]
    for folder in SOURCE_DIRS:
        directory = root / folder
        if directory.exists():
            candidates.extend(directory.rglob("*"))
    for path in sorted(set(candidates)):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in relative.parts):
            continue
        if (path.suffix.lower() in SECRET_SUFFIXES or path.name == "secrets.toml"
                or path.name.endswith(("-wal", "-shm")) or path.name.startswith(".env")):
            continue
        if relative.as_posix() == "scripts/browser_check.mjs":
            # Optional developer QA depends on host skill/browser tooling, not the release.
            continue
        if not path.resolve().is_relative_to(root):
            continue
        yield path, relative.as_posix()


def package(root: Path, output: Path):
    root, output = root.resolve(), output.resolve()
    entries = [(path, name) for path, name in source_files(root) if path.resolve() != output]
    manifest = {"format": "KidSafe source manifest v1", "files": []}
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path, name in entries:
            content = path.read_bytes()
            manifest["files"].append({"path": name, "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()})
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)
        info = zipfile.ZipInfo("MANIFEST.sha256.json", date_time=(2026, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8"))
    return {"archive": str(output), "files": len(entries), "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=Path(".tmp/releases/KidSafe-source.zip"))
    args = parser.parse_args()
    print(json.dumps(package(args.root, args.output), indent=2))
