import re
import sqlite3

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text

from server.app import create_app
from server.config import Settings
from server.models import Account
from server.security import password_hash, password_verify


@pytest.fixture
def signup(tmp_path):
    settings = Settings(f"sqlite:///{tmp_path / 'accounts.db'}", b'a' * 32, b'b' * 32)
    app = create_app(settings)
    with TestClient(app, base_url='https://testserver') as client:
        page = client.get('/register')
        token = re.search(r'name="signup-csrf" content="([^"]+)"', page.text)[1]
        client.headers['X-CSRF-Token'] = token
        yield app, client, settings


def body(**changes):
    data = dict(name='  Nguyễn An  ', username='  an.parent  ', password='family-secret-2026',
                confirm_password='family-secret-2026')
    return {**data, **changes}


def test_signup_requires_login_and_persists_after_restart(signup):
    app, client, settings = signup
    assert client.post('/api/auth/register', json=body()).status_code == 201
    assert client.get('/api/auth/me').status_code == 401
    assert client.get('/app/devices', follow_redirects=False).headers['location'] == '/login'
    with app.state.database.session() as db:
        account = db.scalar(select(Account).where(Account.username == 'an.parent'))
        assert account.role == 'parent' and account.child_id is None
        assert account.password != body()['password'] and password_verify(body()['password'], account.password)
        assert account.display_name_enc != 'Nguyễn An'
        assert app.state.crypto.decrypt(account.display_name_enc) == 'Nguyễn An'
    # A new app instance uses the same durable DB and encryption/signing keys.
    restarted = create_app(settings)
    with TestClient(restarted, base_url='https://testserver') as visitor:
        result = visitor.post('/api/auth/login', json={'username': 'an.parent', 'password': body()['password']})
        assert result.status_code == 200
        assert visitor.get('/api/auth/me').json()['name'] == 'Nguyễn An'
        assert visitor.get('/api/children').json() == []
        assert visitor.get('/app/devices').status_code == 200
        assert 'Nguyễn An' in visitor.get('/app/overview').text
        visitor.headers['X-CSRF-Token'] = result.json()['csrf_token']
        assert visitor.post('/api/auth/logout').status_code == 200
        assert visitor.get('/app/devices', follow_redirects=False).status_code == 303


def test_signup_csrf_origin_and_cookie_flags(signup):
    _, client, _ = signup
    page = client.get('/register')
    cookie = page.headers['set-cookie']
    assert all(flag in cookie for flag in ['HttpOnly', 'Secure', 'SameSite=lax', 'Max-Age=1800'])
    token = re.search(r'name="signup-csrf" content="([^"]+)"', page.text)[1]
    client.headers.pop('X-CSRF-Token')
    assert client.post('/api/auth/register', json=body()).status_code == 403
    client.headers['X-CSRF-Token'] = token
    assert client.post('/api/auth/register', json=body(), headers={'Origin': 'https://elsewhere.example'}).status_code == 403
    assert client.post('/api/auth/register', json=body(), headers={'Sec-Fetch-Site': 'cross-site'}).status_code == 403
    assert client.post('/api/auth/register', json=body(), headers={'Origin': 'https://testserver'}).status_code == 201


def test_signup_validation_duplicate_and_fixed_parent_role(signup):
    app, client, _ = signup
    for changes in [{'password': 'short'}, {'name': '   '}, {'username': 'bad name'},
                    {'role': 'admin'}, {'child_id': 'someone-else'}]:
        response = client.post('/api/auth/register', json=body(**changes))
        assert response.status_code == 422
        assert 'family-secret-2026' not in response.text and 'short' not in response.text
    assert client.post('/api/auth/register', json=body(confirm_password='another-secret')).status_code == 400
    assert client.post('/api/auth/register', json=body()).status_code == 201
    assert client.post('/api/auth/register', json=body(name='Another name')).status_code == 409
    with app.state.database.session() as db:
        assert len(list(db.scalars(select(Account)))) == 1


def test_signup_has_its_own_ip_rate_limit(signup):
    _, client, _ = signup
    for _ in range(10):
        assert client.post('/api/auth/register', json={}).status_code == 422
    assert client.post('/api/auth/register', json={}).status_code == 429
    assert client.post('/api/auth/login', json={'username': 'missing', 'password': 'incorrect'}).status_code == 401


def test_upgrade_old_account_database_without_losing_credentials(tmp_path):
    path = tmp_path / 'old.db'
    with sqlite3.connect(path) as connection:
        connection.execute('CREATE TABLE accounts (id TEXT PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT, child_id TEXT, failures INTEGER, locked_until INTEGER)')
        connection.execute('INSERT INTO accounts VALUES (?, ?, ?, ?, NULL, 0, 0)', ('old', 'existing', password_hash('old-password-2026'), 'parent'))
    app = create_app(Settings(f'sqlite:///{path}', b'a' * 32, b'b' * 32))
    with TestClient(app, base_url='https://testserver') as client:
        assert client.post('/api/auth/login', json={'username': 'existing', 'password': 'old-password-2026'}).status_code == 200
        assert client.get('/api/auth/me').json()['name'] == 'existing'
    with app.state.database.session() as db:
        assert db.execute(text('SELECT MAX(version) FROM schema_versions')).scalar() == 3
