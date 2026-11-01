from app import create_app

app = create_app()

if __name__ == '__main__':
    # Para uso local. Em produção, usar servidor WSGI e HTTPS.
    app.run(host='127.0.0.1', port=5000, debug=False)
