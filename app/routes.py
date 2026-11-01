"""Rotas e regras de negócio. Entradas sempre verificadas no servidor."""
from datetime import date, datetime, timezone
from functools import wraps
import sqlite3

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from .db import get_db

bp = Blueprint('main', __name__)


def login_required(func):
    @wraps(func)
    def protected(*args, **kwargs):
        if not session.get('uid'):
            flash('Faça login para acessar a área administrativa.', 'warning')
            return redirect(url_for('main.login'))
        return func(*args, **kwargs)
    return protected


def form_text(field, max_length, required=False):
    value = request.form.get(field, '').strip()
    if required and not value:
        raise ValueError('Preencha o campo obrigatório: ' + field.replace('_', ' ') + '.')
    if len(value) > max_length:
        raise ValueError(f'O campo {field.replace("_", " ")} deve ter até {max_length} caracteres.')
    return value


def as_date(value, field):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError('Informe uma data válida em ' + field + '.') from None


@bp.route('/')
def catalogo():
    db = get_db()
    search = request.args.get('q', '').strip()[:80]
    status = request.args.get('status', 'todas')
    if status not in ('todas', 'disponiveis', 'emprestadas'):
        status = 'todas'
    sql = 'SELECT * FROM ferramentas WHERE 1=1'
    params = []
    if search:
        safe = search.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')
        sql += " AND (nome LIKE ? ESCAPE '\\' OR codigo LIKE ? ESCAPE '\\')"
        params.extend([f'%{safe}%', f'%{safe}%'])
    if status != 'todas':
        sql += ' AND status = ?'
        params.append('disponivel' if status == 'disponiveis' else 'emprestada')
    sql += ' ORDER BY id ASC'
    ferramentas = db.execute(sql, params).fetchall()
    return render_template('catalogo.html', ferramentas=ferramentas, busca=search, filtro=status, page='catalogo')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = form_text('username', 60).lower()
        password = request.form.get('password', '')
        # A combinação conta + IP tem limite de cinco falhas por 15 minutos.
        ip = request.remote_addr or 'local'
        key = f'{user}|{ip}'
        now = int(datetime.now(timezone.utc).timestamp())
        db = get_db()
        db.execute('DELETE FROM tentativas_login WHERE momento < ?', (now - 900,))
        fails = db.execute('SELECT count(*) AS n FROM tentativas_login WHERE identificador=? AND momento>=?',
                           (key, now-900)).fetchone()['n']
        if fails >= 5:
            flash('Muitas tentativas. Tente novamente em 15 minutos.', 'error')
            return render_template('login.html', page='login'), 429
        row = db.execute('SELECT * FROM usuarios WHERE username=?', (user,)).fetchone()
        if row and check_password_hash(row['password_hash'], password):
            db.execute('DELETE FROM tentativas_login WHERE identificador=?', (key,))
            session.clear()
            session.permanent = True
            session['uid'] = row['id']
            session['nome'] = row['nome']
            session['last_seen'] = now
            flash('Bem-vindo à área administrativa.', 'success')
            return redirect(url_for('main.registrar_emprestimo'))
        db.execute('INSERT INTO tentativas_login (identificador,momento) VALUES (?,?)', (key,now))
        flash('Usuário ou senha inválidos.', 'error')
    return render_template('login.html', page='login')


@bp.post('/logout')
def logout():
    session.clear()
    flash('Você saiu da área administrativa.', 'success')
    return redirect(url_for('main.catalogo'))


@bp.route('/admin')
@login_required
def admin():
    return redirect(url_for('main.registrar_emprestimo'))


@bp.route('/admin/emprestimos/registrar', methods=['GET', 'POST'])
@login_required
def registrar_emprestimo():
    db = get_db()
    if request.method == 'POST':
        try:
            morador_id = int(request.form.get('morador_id', ''))
            ferramenta_id = int(request.form.get('ferramenta_id', ''))
            inicio = as_date(request.form.get('data_emprestimo'), 'Data do empréstimo')
            prazo = as_date(request.form.get('data_prevista'), 'Data prevista')
            observacoes = form_text('observacoes', 300)
            if inicio > date.today():
                raise ValueError('A data do empréstimo não pode estar no futuro.')
            if prazo < inicio:
                raise ValueError('A devolução prevista deve ocorrer na mesma data ou depois do empréstimo.')
            if not db.execute('SELECT id FROM moradores WHERE id=?', (morador_id,)).fetchone():
                raise ValueError('Selecione um morador válido.')
            db.execute('BEGIN IMMEDIATE')
            result = db.execute("UPDATE ferramentas SET status='emprestada' WHERE id=? AND status='disponivel'", (ferramenta_id,))
            if result.rowcount != 1:
                raise ValueError('Esta ferramenta não está disponível para empréstimo.')
            db.execute('''INSERT INTO emprestimos
                (ferramenta_id,morador_id,data_emprestimo,data_prevista,observacoes)
                VALUES (?,?,?,?,?)''', (ferramenta_id,morador_id,inicio.isoformat(),prazo.isoformat(),observacoes))
            db.execute('COMMIT')
            flash('Empréstimo registrado com sucesso.', 'success')
            return redirect(url_for('main.registrar_emprestimo'))
        except (TypeError, ValueError, sqlite3.IntegrityError) as exc:
            if db.in_transaction:
                db.execute('ROLLBACK')
            flash(str(exc) if isinstance(exc, ValueError) else 'Selecione os dados válidos.', 'error')
    moradores = db.execute('SELECT id,nome FROM moradores ORDER BY nome').fetchall()
    ferramentas = db.execute("SELECT id,codigo,nome FROM ferramentas WHERE status='disponivel' ORDER BY nome").fetchall()
    return render_template('emprestimo.html', moradores=moradores, ferramentas=ferramentas,
                           page='emprestimos', today=date.today().isoformat())


@bp.route('/admin/devolucoes')
@login_required
def devolucoes():
    db = get_db()
    search = request.args.get('q', '').strip()[:80]
    situacao = request.args.get('status', 'todos')
    if situacao not in ('todos', 'atrasados', 'no-prazo'):
        situacao = 'todos'
    sql = '''SELECT e.id,e.data_emprestimo,e.data_prevista, f.id AS ferramenta_id,
                f.codigo,f.nome,f.descricao,f.imagem, m.nome AS morador_nome,
                CASE WHEN date(e.data_prevista) < date(?) THEN 'atrasado' ELSE 'no-prazo' END AS situacao
            FROM emprestimos e
            JOIN ferramentas f ON f.id=e.ferramenta_id
            JOIN moradores m ON m.id=e.morador_id
            WHERE e.data_devolucao IS NULL'''
    params = [date.today().isoformat()]
    if search:
        safe = search.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')
        sql += " AND (f.nome LIKE ? ESCAPE '\\' OR m.nome LIKE ? ESCAPE '\\')"
        params.extend([f'%{safe}%',f'%{safe}%'])
    if situacao == 'atrasados':
        sql += ' AND date(e.data_prevista) < date(?)'
        params.append(date.today().isoformat())
    elif situacao == 'no-prazo':
        sql += ' AND date(e.data_prevista) >= date(?)'
        params.append(date.today().isoformat())
    sql += ' ORDER BY e.data_prevista, e.id'
    registros = db.execute(sql, params).fetchall()
    total = db.execute('''SELECT count(*) AS n FROM emprestimos WHERE data_devolucao IS NULL''').fetchone()['n']
    atrasados = db.execute('''SELECT count(*) AS n FROM emprestimos
                WHERE data_devolucao IS NULL AND date(data_prevista) < date(?)''',
                           (date.today().isoformat(),)).fetchone()['n']
    return render_template('devolucoes.html', registros=registros, total=total,
                           atrasados=atrasados, no_prazo=total-atrasados, page='devolucoes',
                           busca=search, situacao=situacao)


@bp.post('/admin/devolucoes/<int:emprestimo_id>')
@login_required
def confirmar_devolucao(emprestimo_id):
    db = get_db()
    try:
        db.execute('BEGIN IMMEDIATE')
        emprestimo = db.execute('''SELECT ferramenta_id FROM emprestimos
                                  WHERE id=? AND data_devolucao IS NULL''', (emprestimo_id,)).fetchone()
        if not emprestimo:
            raise ValueError('O empréstimo já foi devolvido ou não existe.')
        db.execute('UPDATE emprestimos SET data_devolucao=? WHERE id=?', (date.today().isoformat(),emprestimo_id))
        db.execute("UPDATE ferramentas SET status='disponivel' WHERE id=?", (emprestimo['ferramenta_id'],))
        db.execute('COMMIT')
        flash('Devolução registrada. Ferramenta disponível novamente.', 'success')
    except ValueError as exc:
        if db.in_transaction:
            db.execute('ROLLBACK')
        flash(str(exc), 'error')
    return redirect(url_for('main.devolucoes'))


@bp.route('/admin/ferramentas', methods=['GET','POST'])
@login_required
def cad_ferramentas():
    db = get_db()
    if request.method == 'POST':
        try:
            codigo = form_text('codigo', 12, True).upper()
            nome = form_text('nome', 100, True)
            descricao = form_text('descricao', 300)
            imagem = 'generica.svg'
            if 'furadeira' in nome.lower(): imagem = 'furadeira.jpg'
            elif 'escada' in nome.lower(): imagem = 'escada.jpg'
            elif 'martelo' in nome.lower(): imagem = 'martelo.jpg'
            elif 'serra' in nome.lower(): imagem = 'serra.jpg'
            db.execute('INSERT INTO ferramentas (codigo,nome,descricao,imagem) VALUES (?,?,?,?)',
                       (codigo,nome,descricao,imagem))
            flash('Ferramenta cadastrada.', 'success')
            return redirect(url_for('main.cad_ferramentas'))
        except sqlite3.IntegrityError:
            flash('Já existe uma ferramenta com esse código.', 'error')
        except ValueError as exc:
            flash(str(exc), 'error')
    rows = db.execute('SELECT * FROM ferramentas ORDER BY id DESC').fetchall()
    return render_template('cad_ferramentas.html', ferramentas=rows, page='cad_ferramentas')


@bp.route('/admin/moradores', methods=['GET','POST'])
@login_required
def cad_moradores():
    db = get_db()
    if request.method == 'POST':
        try:
            nome = form_text('nome', 100, True)
            contato = form_text('contato', 100)
            db.execute('INSERT INTO moradores (nome,contato) VALUES (?,?)', (nome,contato))
            flash('Morador cadastrado.', 'success')
            return redirect(url_for('main.cad_moradores'))
        except ValueError as exc:
            flash(str(exc), 'error')
    rows = db.execute('SELECT id,nome,contato FROM moradores ORDER BY id DESC').fetchall()
    return render_template('cad_moradores.html', moradores=rows, page='cad_moradores')
