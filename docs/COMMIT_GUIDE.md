# Guia de versionamento

Exemplos de mensagens semânticas para alterações reais:

- `chore: iniciar estrutura do projeto Flask`
- `feat: adicionar modelos e autenticação administrativa`
- `feat: criar catálogo público de ferramentas`
- `feat: permitir registro de empréstimos`
- `feat: controlar devoluções e alertas de atraso`
- `test: validar fluxos públicos e administrativos`
- `docs: documentar execução e riscos do MVP`

Para obter identificadores reais após criar os commits: `git log --date=short --pretty=format:'%h | %s | %ad'`.

Não registre SHA fictício ou commit ainda não realizado como evidência acadêmica.

Sugestão para revisão individual: crie uma branch `feature/testes`, faça alterações pequenas, abra um Pull Request no GitHub, revise o diff e faça o merge após os testes.
