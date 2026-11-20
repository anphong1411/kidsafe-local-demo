import hashlib
import json
import zipfile

from scripts.package_release import package


def test_source_package_excludes_private_data_and_hashes_every_source(tmp_path):
    root = tmp_path / 'source'
    (root / 'server').mkdir(parents=True)
    (root / '.runtime').mkdir()
    (root / 'server' / '__pycache__').mkdir()
    (root / 'docs').mkdir()
    preview_config = root / 'demo' / 'streamlit_preview' / '.streamlit'
    preview_config.mkdir(parents=True)
    (preview_config / 'secrets.toml').write_text('PRIVATE', encoding='utf-8')
    (root / 'README.md').write_text('KidSafe setup', encoding='utf-8')
    (root / 'server' / 'app.py').write_text('print("source")', encoding='utf-8')
    (root / '.runtime' / 'lab.json').write_text('PRIVATE', encoding='utf-8')
    (root / 'server' / 'database.db').write_text('PRIVATE', encoding='utf-8')
    (root / 'server' / '__pycache__' / 'app.pyc').write_text('PRIVATE', encoding='utf-8')
    (root / 'docs' / 'certificate.key').write_text('PRIVATE', encoding='utf-8')
    first = package(root, tmp_path / 'first.zip')
    second = package(root, tmp_path / 'second.zip')
    assert first['sha256'] == second['sha256'] and first['files'] == 2
    with zipfile.ZipFile(first['archive']) as archive:
        assert sorted(archive.namelist()) == ['MANIFEST.sha256.json', 'README.md', 'server/app.py']
        manifest = json.loads(archive.read('MANIFEST.sha256.json'))
        for entry in manifest['files']:
            assert hashlib.sha256(archive.read(entry['path'])).hexdigest() == entry['sha256']
