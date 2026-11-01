# Modelo de dados — Ferramenta Compartilhada

O SQLite executa o esquema em `app/schema.sql`.

| Entidade | Chave primária | Atributos | Papel |
|---|---|---|---|
| `ferramentas` | `id` | `codigo` (único), `nome`, `descricao`, `imagem`, `status` | Catálogo compartilhado |
| `moradores` | `id` | `nome`, `contato` | Responsáveis por empréstimos; acesso restrito |
| `emprestimos` | `id` | `ferramenta_id`, `morador_id`, `data_emprestimo`, `data_prevista`, `data_devolucao`, `observacoes` | Registro histórico |
| `usuarios` | `id` | `username`, `nome`, `password_hash` | Acesso administrativo |
| `tentativas_login` | `id` | `identificador`, `momento` | Limitação de tentativas de login |

## Cardinalidade

- `moradores (1) -> (N) emprestimos`: um morador pode realizar vários empréstimos.
- `ferramentas (1) -> (N) emprestimos`: a ferramenta pode ser emprestada diversas vezes no histórico.
- Um índice parcial impede dois empréstimos **ativos** simultâneos para a mesma ferramenta.

## Integridade

- `data_prevista >= data_emprestimo`.
- `data_devolucao IS NULL` indica empréstimo ativo.
- Devolução encerra o empréstimo e altera `status` para `disponivel` na **mesma transação**.
- O banco não expõe contatos no catálogo público.
- Uso de chaves estrangeiras, `CHECK`, consultas parametrizadas e `BEGIN IMMEDIATE`.

> A tabela `usuarios` representa contas de voluntários. A autenticação para múltiplas associações ainda não faz parte do escopo do MVP.
