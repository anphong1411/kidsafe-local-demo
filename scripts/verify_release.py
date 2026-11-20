"""Verify source archive integrity and extract to a new directory safely."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile


def verify(archive_path: Path, destination: Path | None = None):
    with zipfile.ZipFile(archive_path) as archive:
        if archive.testzip():
            raise ValueError('Archive CRC check failed')
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Duplicate archive members')
        manifest = json.loads(archive.read('MANIFEST.sha256.json'))
        entries = {item['path']: item for item in manifest['files']}
        if set(names) != set(entries) | {'MANIFEST.sha256.json'}:
            raise ValueError('Manifest membership mismatch')
        for name, item in entries.items():
            path = PurePosixPath(name)
            if path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name:
                raise ValueError('Unsafe member path')
            if any(part in {'.runtime', '.venv', '.git', '.env'} for part in path.parts):
                raise ValueError('Private runtime member')
            content = archive.read(name)
            if len(content) != item['bytes'] or hashlib.sha256(content).hexdigest() != item['sha256']:
                raise ValueError('Manifest hash mismatch: ' + name)
        if destination:
            if destination.exists():
                raise ValueError('Extraction destination must be new')
            destination.mkdir(parents=True)
            root = destination.resolve()
            for name in names:
                target = (root / name).resolve()
                if not target.is_relative_to(root):
                    raise ValueError('Extraction escapes destination')
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(name))
    return len(entries)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--extract', type=Path)
    args = parser.parse_args()
    print(f'PASS: {verify(args.archive, args.extract)} source files match manifest; no private runtime files')
