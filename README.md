# Ferramenta Compartilhada

MVP acadêmico em Flask para cadastro e empréstimo comunitário de ferramentas, com catálogo público de disponibilidade, área administrativa, devoluções e alertas de atraso. Projeto relacionado ao **ODS 12 — Consumo e Produção Responsáveis**.

> Em desenvolvimento. A associação e os registros demonstrativos são fictícios; a aplicação não comprova validação real de campo.

## Iniciar localmente

Requisitos: **Python 3.12 ou superior** e acesso à internet para instalar dependências.

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Windows CMD: .venv\Scripts\activate.bat
# macOS/Linux:
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python run.py
```

Abra `http://127.0.0.1:5000`. Na primeira execução, a aplicação cria a base SQLite, alguns **dados fictícios** e uma senha aleatória para o usuário `voluntario`. **Anote a senha exibida no terminal**. Ela não é salva em texto puro.

Os caminhos são:

- `/` — catálogo público.
- `/login` — login do voluntário.
- `/admin/emprestimos/registrar` — registro de empréstimos.
- `/admin/devolucoes` — devoluções e atrasos.
- `/admin/ferramentas` — cadastro de ferramentas.
- `/admin/moradores` — cadastro de moradores.

O domínio `ferramenta-compartilhada.org` mostrado nas imagens acadêmicas é **ilustrativo**: não é URL de hospedagem deste código.

## Prévias visuais

As imagens em `docs/referencias-visuais/` são as três telas fornecidas como referência de design.
As páginas HTML em `docs/previews/` são **apenas prévias estáticas**; servem para consultar o desenho visual sem instalação, mas não gravam empréstimos. A aplicação real deve ser aberta pelo servidor Flask em `localhost:5000`.

## Testes

```bash
python -m pytest -q
```

## Arquitetura

- **Flask/Python**: rotas, permissões, regras de empréstimo.
- **SQLite**: ferramentas, moradores, empréstimos e contas administrativas.
- **Jinja2, HTML, CSS, JavaScript**: telas responsivas inspiradas nas três referências visuais.
- **Segurança inicial**: hash `scrypt` (Werkzeug), verificação de sessão, tokens CSRF, SQL parametrizado, limitação de tentativas de login, dados de moradores restritos.

### Regras de negócio

- O catálogo não mostra dados dos moradores.
- Somente ferramentas disponíveis podem ser emprestadas.
- A mesma ferramenta não pode ter dois empréstimos ativos (índice único parcial no SQLite).
- Devolução encerra o registro e libera a ferramenta.
- Empréstimo ativo com prazo anterior ao dia atual é classificado como atrasado.

## Publicação e proteção de dados

Antes de publicar para pessoas reais: definir `FLASK_SECRET_KEY` em variável de ambiente, configurar HTTPS e `FLASK_HTTPS=1`, usar servidor WSGI apropriado, desabilitar debug, criar backup e armazenamento persistente, revisar a política de privacidade e as permissões dos voluntários. A senha gerada no ambiente de demonstração **não deve ser utilizada em produção**. O projeto não oferece garantia de produção sem avaliação adicional.

## Controle de versão

O diretório pode ser adicionado ao repositório público `ferramenta-compartilhada` no GitHub. Consulte `docs/COMMIT_GUIDE.md` para mensagens semânticas e fluxo de revisão. Os commits locais e os commits publicados no GitHub são eventos diferentes: verifique o SHA remoto antes de preencher a atividade.

## Publicar no GitHub

Leia [`docs/COMO_PUBLICAR_NO_GITHUB.md`](docs/COMO_PUBLICAR_NO_GITHUB.md). O procedimento muda caso o repositório online já tenha um commit inicial. **Não use push forçado.**
