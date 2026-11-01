"""Ferramenta Compartilhada — MVP web em Flask."""
import os
import secrets
from datetime import timedelta, date
from pathlib import Path

from flask import Flask, abort, request, session, g

from .db import close_db, setup_first_run


def create_app(test_config=None):
    root = Path(__file__).resolve().parent.parent
    instance_path = root / 'instance'
    instance_path.mkdir(parents=True, exist_ok=True)
    secret_file = instance_path / '.local-secret'

    secret = os.environ.get('FLASK_SECRET_KEY')
    if not secret:
        if secret_file.exists():
            secret = secret_file.read_text(encoding='utf-8')
        else:
            secret = secrets.token_hex(32)
            secret_file.write_text(secret, encoding='utf-8')
            secret_file.chmod(0o600)

    app = Flask(__name__, instance_path=str(instance_path))
    app.config.update(
        SECRET_KEY=secret,
        DATABASE=os.environ.get('DATABASE_PATH', str(instance_path / 'ferramentas.sqlite3')),
        DEMO_MODE=os.environ.get('DEMO_MODE', '1') == '1',
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=os.environ.get('FLASK_HTTPS', '0') == '1',
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
        MAX_CONTENT_LENGTH=32 * 1024,
    )
    if test_config:
        app.config.update(test_config)

    app.teardown_appcontext(close_db)

    @app.context_processor
    def inject_template_helpers():
        def csrf_token():
            if 'csrf_token' not in session:
                session['csrf_token'] = secrets.token_urlsafe(32)
            return session['csrf_token']
        return {'csrf_token': csrf_token, 'hoje': date.today()}

    @app.template_filter('data_br')
    def data_br(value):
        if not value:
            return '—'
        try:
            return date.fromisoformat(str(value)).strftime('%d/%m/%Y')
        except ValueError:
            return str(value)

    @app.before_request
    def security_checks():
        from datetime import datetime, timezone
        if session.get('uid'):
            last_seen = session.get('last_seen', 0)
            now = int(datetime.now(timezone.utc).timestamp())
            if now - last_seen > 1800:
                session.clear()
            else:
                session['last_seen'] = now
        if request.method == 'POST':
            provided = request.form.get('csrf_token', '')
            expected = session.get('csrf_token', '')
            if not expected or not secrets.compare_digest(str(provided), str(expected)):
                abort(400, description='Solicitação inválida. Recarregue a página e tente novamente.')

    @app.after_request
    def default_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; form-action 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'"
        if request.path.startswith('/admin') or request.path == '/login':
            response.headers['Cache-Control'] = 'no-store'
        return response

    from .routes import bp
    app.register_blueprint(bp)

    @app.errorhandler(400)
    def bad_request(error):
        return {'erro': 'Solicitação inválida.', 'detalhe': getattr(error,'description','')}, 400

    if not app.config.get('TESTING', False):
        setup_first_run(app)
    return app
