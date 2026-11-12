# FinanceTracker — Guia de acesso e manipulação do PostgreSQL

**Ambiente local:** PostgreSQL 17, serviço Compose `db`, container `financetracker-db`, base e utilizador `financetracker`, porta `127.0.0.1:5432`.

## 1. Componentes

```text
FastAPI (Ubuntu; ligação prevista para Dia 3)
  → SQLAlchemy (ORM) → Psycopg (driver)
  → 127.0.0.1:5432 → PostgreSQL (container Docker)
                               → volume postgres_data
```

PostgreSQL é a base de dados; `psql` é o cliente SQL; SQLAlchemy e Psycopg serão usados pelo backend Python. O volume mantém tabelas permanentes após recriar o container.

## 2. Iniciar e verificar

Na raiz do repositório:

```bash
docker compose up -d db
docker compose ps
docker compose exec db pg_isready -U financetracker -d financetracker
```

- `up`: cria/inicia; `-d`: segundo plano; `db`: serviço Compose.
- `ps`: lista containers e estados.
- `exec db`: executa um programa no container do serviço.
- `pg_isready`: testa se o servidor aceita ligações.
- `-U`: utilizador; `-d`: base indicada.

**Atenção:** `pg_isready` não confirma necessariamente se a base ou o utilizador existem. No exercício, `-d financertracker` foi escrito incorretamente e mesmo assim apareceu `accepting connections`.

## 3. Aceder com psql

```bash
docker compose exec db psql -U financetracker -d financetracker
```

- `psql`: cliente interativo PostgreSQL.
- `-U financetracker`: utilizador.
- `-d financetracker`: base.

Prompt esperado: `financetracker=#`.

```sql
SELECT current_database();
SELECT current_user;
SELECT version();
```

- `SELECT`: executa consulta.
- `current_database()`: função que devolve a base atual.
- `current_user`: identidade do utilizador atual.
- `version()`: versão do servidor.
- `;`: termina instrução SQL.

No exercício, `current_user` devolveu `financetracker`.

## 4. Metacomandos do psql

| Comando | Significado |
|---|---|
| `\l` | Lista bases de dados. |
| `\dt` | Lista tabelas visíveis. |
| `\d nome_tabela` | Descreve uma tabela. |
| `\conninfo` | Mostra informações da ligação. |
| `\?` | Ajuda dos metacomandos. |
| `\h SELECT` | Ajuda sobre SQL `SELECT`. |
| `\r` | Limpa instrução SQL ainda não executada. |
| `\q` | Sai do psql. |

Metacomandos com `\` normalmente não precisam de `;`.

**Prompt `financetracker-#`:** indica que a instrução continua aberta. O erro `SELECT current_database():` utilizou `:` em vez de `;`. Para recuperar, digitar `\r` e repetir com `;`, ou cancelar a entrada com `Ctrl+C`.

## 5. Exercício realizado: tabela temporária

```sql
CREATE TEMP TABLE test_transactions (
    id INTEGER,
    description VARCHAR(100),
    amount NUMERIC(12, 2)
);
```

- `CREATE TABLE`: cria tabela.
- `TEMP`: tabela temporária da sessão atual.
- `INTEGER`: inteiro.
- `VARCHAR(100)`: texto com até 100 caracteres.
- `NUMERIC(12, 2)`: número decimal exato com precisão 12 e duas casas decimais.

Resultado observado: `CREATE TABLE`.

### Inserir

```sql
INSERT INTO test_transactions (id, description, amount)
VALUES (1, 'Supermercado', 45.90);
```

- `INSERT INTO`: insere registo.
- `(id, description, amount)`: colunas de destino (boa prática; no exercício original foram omitidas).
- `VALUES`: valores correspondentes às colunas.
- `'Supermercado'`: literal de texto SQL; `45.90`: número.
- `;`: pode estar na linha seguinte; até aparecer, o `psql` aguarda.

Resultado observado no exercício: `INSERT 0 1` — uma linha inserida; `0` é campo OID legado do resultado.

### Consultar

```sql
SELECT * FROM test_transactions;
```

- `SELECT`: consulta.
- `*`: todas as colunas.
- `FROM`: tabela consultada.

Resultado observado:

```text
 id | description  | amount
----+--------------+--------
  1 | Supermercado | 45.90
```

## 6. Outras operações SQL (exemplos para praticar)

### Selecionar e filtrar

```sql
SELECT description, amount
FROM test_transactions
WHERE amount > 20
ORDER BY amount DESC;
```

- `WHERE`: filtra linhas; `>`: maior que.
- `ORDER BY`: ordena resultados; `DESC`: decrescente (`ASC`: crescente).

### Atualizar

```sql
UPDATE test_transactions
SET amount = 49.90
WHERE id = 1;
```

- `UPDATE`: modifica registos; `SET`: define valor; `WHERE`: restringe as linhas.

### Eliminar

```sql
DELETE FROM test_transactions
WHERE id = 1;
```

- `DELETE FROM`: elimina linhas; `WHERE`: restringe quais.
- **Cuidado:** sem `WHERE`, `UPDATE` e `DELETE` podem afetar todas as linhas.

## 7. Tabelas temporárias e persistência

| | `CREATE TEMP TABLE` | `CREATE TABLE` |
|---|---|---|
| Duração | Sessão atual | Até remoção explícita |
| Após `\q` | Desaparece | Permanece |
| Após recriar container com mesmo volume | Não permanece | Permanece normalmente |

Para demonstrar, sair com `\q`, entrar novamente no `psql` e executar `SELECT * FROM test_transactions;`. Espera-se `relation "test_transactions" does not exist`.

Isso **não significa** perda de dados do volume: a tabela foi criada como temporária.

## 8. Gestão do serviço e proteção dos dados

```bash
docker compose stop db
docker compose start db
docker compose up -d db
docker compose down
```

- `stop`: para sem remover.
- `start`: inicia container existente.
- `up -d`: cria/inicia ou recria se necessário.
- `down`: remove containers e rede, mas preserva volumes nomeados por padrão.

**Evitar:**

```bash
docker compose down -v
```

`-v` remove volumes nomeados declarados e volumes anónimos associados, podendo apagar a base de dados.

## 9. Ligação futura do FastAPI (Dia 3)

Formato da URL SQLAlchemy + Psycopg:

```text
postgresql+psycopg://USUARIO:SENHA@HOST:PORTA/BASE
```

Exemplo **apenas local**, com credencial de desenvolvimento:

```text
postgresql+psycopg://financetracker:dev_password@127.0.0.1:5432/financetracker
```

- `postgresql+psycopg`: dialeto e driver.
- `financetracker`: utilizador.
- `dev_password`: senha de exemplo do Compose.
- `127.0.0.1`: host quando Python corre no Ubuntu.
- `5432`: porta local.
- `/financetracker`: nome da base.

Se o backend estiver noutro container na mesma rede Compose, o host será normalmente `db` (nome do serviço), não `127.0.0.1`. Nunca versionar credenciais reais; usar variáveis de ambiente e `.gitignore`.

**A ligação Python–PostgreSQL ainda não foi implementada neste Dia 2.**

## 10. Diagnóstico de problemas

```bash
docker compose ps
docker compose logs db
docker compose exec db pg_isready -U financetracker -d financetracker
docker compose exec db psql -U financetracker -d financetracker
```

- `logs db`: mensagens do serviço.
- `pg_isready`: prontidão do servidor.
- `psql`: verifica uma ligação SQL real.

Para investigar ocupação da porta:

```bash
ss -ltn | grep ':5432'
```

- `ss`: inspeciona sockets; `-l`: em escuta; `-t`: TCP; `-n`: portas numéricas; `grep`: filtra linhas.

**Nota:** mudar `POSTGRES_DB`, `POSTGRES_USER` ou `POSTGRES_PASSWORD` no Compose depois de inicializado um volume não recria automaticamente a base ou as credenciais. Não apagar o volume por impulso.

## 11. Próximos passos

1. Criar modelos `User` e `Transaction` com SQLAlchemy.
2. Configurar `Engine` e sessões.
3. Criar migração inicial com Alembic.
4. Integrar a camada de dados ao FastAPI.

**Referências:** https://www.postgresql.org/docs/17/app-psql.html · https://www.postgresql.org/docs/17/sql.html · https://docs.docker.com/compose/ · https://docs.sqlalchemy.org/
