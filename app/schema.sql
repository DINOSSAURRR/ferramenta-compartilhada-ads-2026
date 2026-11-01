PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS usuarios (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  nome TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ferramentas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  codigo TEXT NOT NULL UNIQUE,
  nome TEXT NOT NULL,
  descricao TEXT NOT NULL DEFAULT '',
  imagem TEXT NOT NULL DEFAULT 'generica.svg',
  status TEXT NOT NULL DEFAULT 'disponivel' CHECK(status IN ('disponivel','emprestada','manutencao')),
  criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS moradores (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nome TEXT NOT NULL,
  contato TEXT NOT NULL DEFAULT '',
  criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS emprestimos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ferramenta_id INTEGER NOT NULL REFERENCES ferramentas(id) ON DELETE RESTRICT,
  morador_id INTEGER NOT NULL REFERENCES moradores(id) ON DELETE RESTRICT,
  data_emprestimo TEXT NOT NULL,
  data_prevista TEXT NOT NULL,
  data_devolucao TEXT DEFAULT NULL,
  observacoes TEXT NOT NULL DEFAULT '',
  criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CHECK(data_prevista >= data_emprestimo),
  CHECK(data_devolucao IS NULL OR data_devolucao >= data_emprestimo)
);
CREATE UNIQUE INDEX IF NOT EXISTS uniq_emprestimo_ativo_por_ferramenta
  ON emprestimos(ferramenta_id) WHERE data_devolucao IS NULL;
CREATE INDEX IF NOT EXISTS idx_emprestimos_prazo ON emprestimos(data_prevista, data_devolucao);

CREATE TABLE IF NOT EXISTS tentativas_login (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  identificador TEXT NOT NULL,
  momento INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tentativas_login ON tentativas_login(identificador,momento);
