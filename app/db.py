"""SQLite, migração inicial e dados de demonstração fictícios."""
import secrets
import sqlite3
from datetime import date, timedelta
from pathlib import Path

from flask import current_app, g
from werkzeug.security import generate_password_hash


def get_db():
    if "db" not in g:
        db = sqlite3.connect(current_app.config["DATABASE"], timeout=10, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        db.execute("PRAGMA busy_timeout = 5000")
        g.db = db
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    script = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
    get_db().executescript(script)


def create_admin(username: str, password: str, display_name="Voluntário"):
    if len(password) < 12:
        raise ValueError("A senha deve ter pelo menos 12 caracteres.")
    get_db().execute(
        "INSERT INTO usuarios (username, nome, password_hash) VALUES (?, ?, ?)",
        (username, display_name, generate_password_hash(password, method="scrypt:32768:8:1")),
    )


def seed_demo():
    """Nunca usar estes cadastros em produção. São apenas dados de exercício."""
    db = get_db()
    if db.execute("SELECT 1 FROM ferramentas LIMIT 1").fetchone():
        return
    ferramentas = [
        ("F001", "Furadeira elétrica", "Furadeira para perfurações em madeira, metal e alvenaria.", "furadeira.jpg", "disponivel"),
        ("E002", "Escada de alumínio", "Escada dobrável de 6 degraus, ideal para pequenos reparos.", "escada.jpg", "emprestada"),
        ("M003", "Martelo", "Martelo de uso geral, indicado para pequenos reparos e montagens.", "martelo.jpg", "disponivel"),
        ("S004", "Serra circular", "Serra circular de 185 mm para cortes em madeira.", "serra.jpg", "emprestada"),
        ("T005", "Trena de medição", "Trena de 5 metros para medidas domésticas.", "generica.svg", "emprestada"),
    ]
    db.executemany("INSERT INTO ferramentas (codigo,nome,descricao,imagem,status) VALUES (?,?,?,?,?)", ferramentas)
    db.executemany("INSERT INTO moradores (nome,contato) VALUES (?,?)", [
        ("Morador 001", ""), ("Morador 002", ""), ("Morador 003", ""), ("Morador 004", "")
    ])
    today = date.today()
    loans = [
        ("E002", "Morador 002", today-timedelta(days=7), today-timedelta(days=2)),
        ("S004", "Morador 003", today-timedelta(days=1), today+timedelta(days=7)),
        ("T005", "Morador 001", today-timedelta(days=2), today+timedelta(days=4)),
    ]
    for code, nome, start, due in loans:
        tool = db.execute("SELECT id FROM ferramentas WHERE codigo=?", (code,)).fetchone()
        user = db.execute("SELECT id FROM moradores WHERE nome=?", (nome,)).fetchone()
        db.execute("INSERT INTO emprestimos (ferramenta_id,morador_id,data_emprestimo,data_prevista) VALUES (?,?,?,?)",
                   (tool["id"],user["id"],start.isoformat(),due.isoformat()))


def setup_first_run(app):
    """Inicialização local idempotente; jamais inventa uma senha fixa no código."""
    database_file = Path(app.config["DATABASE"])
    database_file.parent.mkdir(parents=True, exist_ok=True)
    is_new = not database_file.exists()
    with app.app_context():
        init_db()
        if is_new and app.config.get("DEMO_MODE", False):
            seed_demo()
        if is_new:
            password = secrets.token_urlsafe(18)
            create_admin("voluntario", password, "Voluntário")
            print("\n" + "="*64)
            print("FERRAMENTA COMPARTILHADA — PRIMEIRO ACESSO LOCAL")
            print("Usuário: voluntario")
            print("Senha provisória: " + password)
            print("Anote essa senha; ela não será exibida novamente.")
            print("="*64 + "\n")
