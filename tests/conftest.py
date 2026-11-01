from pathlib import Path
import pytest
from app import create_app
from app.db import init_db, seed_demo, create_admin


@pytest.fixture()
def app(tmp_path):
    application = create_app({
        'TESTING': True,
        'SECRET_KEY': 'somente-teste-chave-super-secreta',
        'DATABASE': str(tmp_path / 'testes.sqlite3'),
        'SESSION_COOKIE_SECURE': False,
        'DEMO_MODE': False,
    })
    with application.app_context():
        init_db()
        seed_demo()
        create_admin('voluntario', 'SenhaForteDeTeste!123')
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()


def token(client):
    """Obtém o token criado no GET anterior sem desabilitar CSRF nos testes."""
    with client.session_transaction() as session:
        return session['csrf_token']


def login(client):
    client.get('/login')
    return client.post('/login', data={
        'csrf_token': token(client), 'username': 'voluntario',
        'password': 'SenhaForteDeTeste!123'
    }, follow_redirects=True)
