import base64
import json

from cryptography import x509
from sqlalchemy import create_engine, text

from scripts.create_lab_tls import generate
from scripts.export_public_config import export
from scripts.seed_lab import seed


def make_profile(directory):
    import secrets
    directory.mkdir()
    pin = generate(directory / 'tls', ['192.168.1.10'])
    values = {
        'KIDSAFE_DATABASE_URL': 'sqlite:///' + (directory / 'db.sqlite').as_posix(),
        'KIDSAFE_ENCRYPTION_KEY': base64.b64encode(secrets.token_bytes(32)).decode(),
        'KIDSAFE_SIGNING_SEED': base64.b64encode(secrets.token_bytes(32)).decode(),
        'demo_username': 'parent@kidsafe.local', 'demo_password': secrets.token_urlsafe(20),
        'certificate_pin_sha256': pin}
    path = directory / 'lab.json'
    path.write_text(json.dumps(values), encoding='utf-8')
    return path, values


def test_seed_profiles_stay_separate_and_idempotent(tmp_path, monkeypatch):
    for key in ('KIDSAFE_DATABASE_URL', 'KIDSAFE_ENCRYPTION_KEY', 'KIDSAFE_SIGNING_SEED'):
        monkeypatch.setenv(key, '')
    first, first_config = make_profile(tmp_path / 'local')
    second, second_config = make_profile(tmp_path / 'lan')
    seed(first)
    seed(second)
    seed(second)
    ids = []
    for config in (first_config, second_config):
        engine = create_engine(config['KIDSAFE_DATABASE_URL'])
        with engine.connect() as db:
            rows = db.execute(text('SELECT id FROM accounts')).all()
            assert len(rows) == 1
            ids.append(rows[0][0])
        engine.dispose()
    assert ids[0] != ids[1]


def test_export_uses_chosen_profile_and_contains_only_public_material(tmp_path, monkeypatch):
    for key in ('KIDSAFE_DATABASE_URL', 'KIDSAFE_ENCRYPTION_KEY', 'KIDSAFE_SIGNING_SEED'):
        monkeypatch.setenv(key, '')
    profile, config = make_profile(tmp_path / 'lan')
    output = export(profile)
    assert set(p.name for p in output.iterdir()) == {'ca.crt', 'server-public.json'}
    public = json.loads((output / 'server-public.json').read_text())
    assert set(public) == {'certificate_pin', 'signing_public_key'}
    assert public['certificate_pin'] == config['certificate_pin_sha256']
    assert len(base64.b64decode(public['signing_public_key'])) == 32
    assert (output / 'ca.crt').read_bytes() == (profile.parent / 'tls/ca.crt').read_bytes()
    cert = x509.load_pem_x509_certificate((profile.parent / 'tls/server.crt').read_bytes())
    san = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
    assert '192.168.1.10' in [str(ip) for ip in san.get_values_for_type(x509.IPAddress)]
