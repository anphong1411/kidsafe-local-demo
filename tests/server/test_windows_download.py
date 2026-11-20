from fastapi.testclient import TestClient

from scripts.create_lab_tls import generate
from test_backend import child, lab


def test_public_download_serves_only_the_configured_windows_file(lab, tmp_path, monkeypatch):
    app, _ = lab
    setup = tmp_path / 'KidSafe-Setup-x64.exe'
    monkeypatch.setattr('dashboard.routes.WINDOWS_SETUP', setup)
    with TestClient(app, base_url='https://testserver') as visitor:
        assert 'Bộ cài chưa có' in visitor.get('/download').text
        assert visitor.get('/download/windows').status_code == 404
        setup.write_bytes(b'MZ test setup')
        assert 'href="/download/windows"' in visitor.get('/download').text
        download = visitor.get('/download/windows')
        assert download.content == setup.read_bytes()
        assert 'KidSafe-Setup-x64.exe' in download.headers['Content-Disposition']


def test_pairing_profile_is_parent_only_and_exports_no_secrets(lab, tmp_path):
    app, parent = lab
    child_id = child(parent)
    credentials = {'username': 'setup-child', 'password': 'test-child-secret'}
    parent.post(f'/api/children/{child_id}/account', json=credentials).raise_for_status()
    local = tmp_path / 'local'
    generate(local, [])
    app.state.pairing_tls = (local / 'ca.crt', local / 'server.crt', 8444)
    assert parent.get('/app/pairing-profile').status_code == 409
    lan = tmp_path / 'lan'
    pin = generate(lan, ['192.168.1.10'])
    app.state.pairing_tls = (lan / 'ca.crt', lan / 'server.crt', 8444)
    with TestClient(app, base_url='https://testserver') as visitor:
        assert visitor.get('/app/pairing-profile').status_code == 401
        visitor.post('/api/auth/login', json=credentials).raise_for_status()
        assert visitor.get('/app/pairing-profile').status_code == 403
    response = parent.get('/app/pairing-profile')
    response.raise_for_status()
    assert response.json() == {
        'format': 'kidsafe-pairing-v1',
        'server_url': 'https://192.168.1.10:8444',
        'ca_pem': (lan / 'ca.crt').read_text(),
        'certificate_pin': pin,
        'signing_public_key': app.state.crypto.envelope({})['public_key'],
    }
    assert 'attachment' in response.headers['Content-Disposition']
