from datetime import date, timedelta
from app.db import get_db
from conftest import login, token


def test_catalogo_publico_e_privacidade(client):
    response = client.get('/')
    assert response.status_code == 200
    assert 'F001 - Furadeira elétrica'.encode() in response.data
    assert b'Morador 001' not in response.data
    assert b'contato' not in response.data.lower()


def test_catalogo_filtros(client):
    response = client.get('/?status=disponiveis&q=furadeira')
    assert b'F001 - Furadeira' in response.data
    assert b'E002 - Escada' not in response.data
    response2 = client.get('/?status=emprestadas')
    assert b'E002 - Escada' in response2.data
    assert b'F001 - Furadeira' not in response2.data


def test_sem_login_administracao_protegida(client):
    for path in ('/admin', '/admin/emprestimos/registrar', '/admin/devolucoes',
                 '/admin/moradores', '/admin/ferramentas'):
        assert client.get(path).status_code == 302


def test_login_valido_e_hash_scrypt(client, app):
    response = login(client)
    assert response.status_code == 200
    assert b'Registrar empr' in response.data
    with app.app_context():
        saved = get_db().execute("SELECT password_hash FROM usuarios WHERE username='voluntario'").fetchone()
        assert saved['password_hash'].startswith('scrypt:')
        assert 'SenhaForteDeTeste!123' not in saved['password_hash']


def test_emprestar_e_devolver_altera_catalogo(client, app):
    login(client)
    client.get('/admin/emprestimos/registrar')
    today = date.today()
    response = client.post('/admin/emprestimos/registrar', data={
        'csrf_token': token(client),
        'morador_id': '1', 'ferramenta_id': '1',
        'data_emprestimo': today.isoformat(),
        'data_prevista': (today + timedelta(days=4)).isoformat(),
        'observacoes': 'Teste acadêmico'
    }, follow_redirects=True)
    assert b'Empr' in response.data and b'sucesso' in response.data
    with app.app_context():
        db = get_db()
        assert db.execute('SELECT status FROM ferramentas WHERE id=1').fetchone()['status'] == 'emprestada'
        record = db.execute('SELECT id FROM emprestimos WHERE ferramenta_id=1 AND data_devolucao IS NULL').fetchone()
    duplicate = client.post('/admin/emprestimos/registrar', data={
        'csrf_token': token(client), 'morador_id': '1', 'ferramenta_id': '1',
        'data_emprestimo': today.isoformat(), 'data_prevista': today.isoformat(),
    }, follow_redirects=True)
    assert b'n' in duplicate.data
    with app.app_context():
        assert get_db().execute('SELECT count(*) AS n FROM emprestimos WHERE ferramenta_id=1 AND data_devolucao IS NULL').fetchone()['n'] == 1
    final = client.post(f'/admin/devolucoes/{record["id"]}', data={'csrf_token': token(client)}, follow_redirects=True)
    assert b'devolu' in final.data.lower()
    with app.app_context():
        assert get_db().execute('SELECT status FROM ferramentas WHERE id=1').fetchone()['status'] == 'disponivel'
        assert get_db().execute('SELECT data_devolucao FROM emprestimos WHERE id=?', (record['id'],)).fetchone()['data_devolucao'] == today.isoformat()


def test_csrf_obrigatorio(client):
    login(client)
    response = client.post('/admin/moradores', data={'nome':'Teste sem token'})
    assert response.status_code == 400


def test_alertas_calculados(client):
    login(client)
    response = client.get('/admin/devolucoes')
    assert response.status_code == 200
    assert b'Atrasado' in response.data
    assert b'No prazo' in response.data
    assert b'Morador 002' in response.data


def test_xss_escapado(client):
    login(client)
    client.get('/admin/ferramentas')
    response = client.post('/admin/ferramentas', data={
        'csrf_token': token(client), 'codigo':'Z999',
        'nome':'Teste XSS', 'descricao':'<script>alert(1)</script>'
    }, follow_redirects=True)
    assert response.status_code == 200
    public = client.get('/?q=Teste%20XSS')
    assert b'&lt;script&gt;' in public.data
    assert b'<script>alert(1)</script>' not in public.data


def test_login_bloqueio_repeticao(client):
    client.get('/login')
    for _ in range(5):
        res = client.post('/login', data={'csrf_token':token(client),'username':'voluntario','password':'errada'})
        assert res.status_code == 200
    response = client.post('/login', data={'csrf_token':token(client),'username':'voluntario','password':'errada'})
    assert response.status_code == 429
