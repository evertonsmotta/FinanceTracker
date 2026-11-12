# FinanceTracker — Day 02: Database Setup

**Duração estimada:** 45–60 minutos  
**Pré-requisito:** Dia 1 concluído (`day-01-architecture-setup.md`)  
**Objetivo:** compreender a modelação relacional, executar PostgreSQL com Docker Compose, instalar as dependências Python e realizar consultas SQL iniciais.

> **Escopo:** neste dia não vamos implementar autenticação, modelos SQLAlchemy ou migrações. Esses assuntos serão tratados nas etapas seguintes.

## 1. Arquitetura e conceitos

Fluxo planeado:

```text
Browser / Angular (futuro)
         |
      HTTP/JSON
         |
   FastAPI (backend)
         |
 SQLAlchemy (ORM)
         |
  Psycopg (driver)
         |
 PostgreSQL (Docker)
```

- **PostgreSQL:** sistema de gestão de bases de dados relacionais (*Relational Database Management System — RDBMS*).
- **SQLAlchemy:** biblioteca Python que fornece ferramentas SQL e mapeamento objeto-relacional (*Object-Relational Mapping — ORM*). Não é uma base de dados.
- **Psycopg:** driver que permite ao Python comunicar com PostgreSQL.
- **Alembic:** ferramenta para versionar alterações no esquema da base de dados (*Database Migrations*).
- **Docker Compose:** define e executa serviços em containers através de um ficheiro YAML.

## 2. Modelo de dados inicial (planeado)

### `users`

| Campo | Tipo sugerido | Observação |
|---|---|---|
| `id` | UUID | Chave primária (*Primary Key — PK*) |
| `name` | VARCHAR | Nome do utilizador |
| `email` | VARCHAR | Valor único (*Unique Constraint*) |
| `password_hash` | VARCHAR | Nunca armazenar a palavra-passe em texto simples |
| `created_at` | TIMESTAMP | Data de criação |

### `transactions`

| Campo | Tipo sugerido | Observação |
|---|---|---|
| `id` | UUID | Chave primária |
| `user_id` | UUID | Chave estrangeira (*Foreign Key — FK*) para `users.id` |
| `description` | VARCHAR | Descrição |
| `amount` | NUMERIC(12,2) | Valor monetário |
| `type` | VARCHAR | Receita ou despesa |
| `category` | VARCHAR | Categoria |
| `date` | DATE | Data da transação |

**Relação:** um utilizador pode possuir muitas transações (*One-to-Many*); cada transação pertence a um utilizador.

**Pergunta de revisão:** por que `transactions.user_id` é uma chave estrangeira?

## 3. Verificar Docker

Na raiz do repositório `FinanceTracker/`:

```bash
docker --version
docker compose version
```

Se o Docker apresentar um erro de permissões, diagnosticar antes de alterar a configuração do sistema.

## 4. Criar `compose.yaml`

Criar o ficheiro **na raiz do repositório**, ao lado de `backend/`, `frontend/` e `docs/`:

```yaml
services:
  db:
    image: postgres:17
    container_name: financetracker-db
    restart: unless-stopped
    environment:
      POSTGRES_USER: financetracker
      POSTGRES_PASSWORD: dev_password
      POSTGRES_DB: financetracker
    ports:
      - "127.0.0.1:5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**Explicação:**

- `image`: imagem utilizada para criar o container.
- `environment`: configuração inicial da base de dados.
- `ports`: disponibiliza a porta PostgreSQL apenas no computador local.
- `volumes`: mantém os dados entre recriações do container.
- `restart`: política de reinício do serviço.

> **Segurança:** `dev_password` é uma credencial didática, adequada apenas a um ambiente local de aprendizagem. Não reutilizar em produção. Futuramente, mover as credenciais para variáveis de ambiente não versionadas.
>
> **Atenção:** se a porta 5432 já estiver ocupada, será necessário ajustar o mapeamento da porta no host e, depois, a configuração da ligação Python.

## 5. Iniciar e verificar PostgreSQL

Executar **na raiz do repositório**:

```bash
docker compose up -d db
docker compose ps
docker compose logs db
```

Procurar nos logs uma mensagem semelhante a:

```text
database system is ready to accept connections
```

Entrar no cliente SQL (*psql*):

```bash
docker compose exec db psql -U financetracker -d financetracker
```

Dentro do `psql`, executar:

```sql
SELECT version();
SELECT current_database();
SELECT current_user;
```

Comandos úteis do `psql`:

```text
\l  -- listar bases de dados
\dt -- listar tabelas da base de dados atual
\q  -- sair
```

## 6. Instalar as dependências Python

No terminal, entrar no backend e ativar o ambiente virtual:

```bash
cd backend
source .venv/bin/activate
python -m pip install sqlalchemy 'psycopg[binary]' alembic
```

Verificar a instalação:

```bash
python -m pip show sqlalchemy psycopg alembic
```

**Decisão didática:** começaremos com SQLAlchemy síncrono. A utilização de sessões assíncronas (*AsyncSession*) ficará para uma etapa posterior.

## 7. Exercício SQL — tabela temporária

Dentro do `psql`, criar uma tabela temporária:

```sql
CREATE TEMP TABLE test_transactions (
    id INTEGER,
    description VARCHAR(100),
    amount NUMERIC(12, 2)
);
```

Inserir um registo:

```sql
INSERT INTO test_transactions
VALUES (1, 'Supermercado', 45.90);
```

Consultar:

```sql
SELECT * FROM test_transactions;
```

Resultado esperado:

```text
 id | description  | amount
----+--------------+--------
  1 | Supermercado | 45.90
```

**Importante:** a tabela `TEMP` existe apenas durante a sessão atual do PostgreSQL. Se saíres do `psql` e voltares a entrar, terás de a criar novamente.

### Questões de consolidação

1. Qual é a diferença entre uma imagem Docker e um container?
2. Para que serve um volume Docker?
3. Qual é a diferença entre chave primária (*PK*) e chave estrangeira (*FK*)?
4. Por que utilizar `NUMERIC(12,2)` para valores monetários em PostgreSQL?
5. O que diferencia SQLAlchemy de PostgreSQL?
6. O que acontece à tabela temporária quando a sessão `psql` termina?

## 8. Checklist

- [ ] Compreender a relação entre `users` e `transactions`.
- [ ] Verificar Docker e Docker Compose.
- [ ] Criar `compose.yaml` na raiz do repositório.
- [ ] Iniciar PostgreSQL com `docker compose up -d db`.
- [ ] Confirmar o estado do container com `docker compose ps`.
- [ ] Verificar nos logs que PostgreSQL aceita ligações.
- [ ] Entrar no `psql` e executar consultas de identificação.
- [ ] Instalar SQLAlchemy, Psycopg e Alembic no `.venv` do backend.
- [ ] Criar, preencher e consultar `test_transactions`.

## 9. Entrega para revisão (*Code Review*)

Enviar:

1. O conteúdo de `compose.yaml` (sem credenciais reais).
2. A saída de `docker compose ps`.
3. A saída de `SELECT * FROM test_transactions;` **antes de encerrar o `psql`**.
4. Eventuais erros e as soluções tentadas.

## 10. Próxima etapa — Day 03

- Configurar a ligação FastAPI ↔ PostgreSQL.
- Criar modelos com SQLAlchemy.
- Preparar e executar a primeira migração com Alembic.
- Avançar gradualmente para o registo de utilizadores.

---

**Princípio-chave:** Docker executa PostgreSQL; PostgreSQL persiste os dados; Psycopg realiza a comunicação com Python; SQLAlchemy organiza o acesso aos dados; Alembic controla a evolução do esquema.
