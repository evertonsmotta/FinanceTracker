# FinanceTracker — Dia 3: Lições aprendidas

**Tema:** SQLAlchemy ORM, ligação ao PostgreSQL, modelos, Alembic e persistência de dados  
**Estado:** Concluído — primeira migração aplicada e primeiro utilizador inserido e consultado.  
**Ambiente:** Ubuntu, Python 3.12 (`.venv`), SQLAlchemy 2.1.8, PostgreSQL 17 em Docker, Psycopg 3, Alembic.

> Este documento regista o trabalho realizado no Dia 3. Os exemplos de credenciais são exclusivamente locais e não devem ser usados em produção.

## 1. Objetivos alcançados

- Confirmar o PostgreSQL em execução através do Docker Compose.
- Confirmar que o SQLAlchemy está disponível no ambiente virtual.
- Criar `app/database.py` e testar uma ligação real à base de dados.
- Definir o modelo ORM `User` com quatro colunas.
- Inicializar e configurar o Alembic.
- Gerar, rever e aplicar a primeira migração.
- Inserir e consultar um utilizador através de uma `Session`.
- Confirmar a persistência com uma consulta SQL diretamente no PostgreSQL.

## 2. Arquitetura e fluxo de dados

```mermaid
flowchart TD
    A[Aplicação Python / FastAPI] --> B[SQLAlchemy ORM]
    B --> C[Engine / Connection Pool]
    C --> D[Psycopg — driver]
    D --> E[(PostgreSQL 17 — Docker)]
    F[Alembic — migrações] --> B
    F --> E
```

- **PostgreSQL:** sistema de gestão de base de dados (Database Management System — DBMS) que armazena os dados.
- **SQLAlchemy:** biblioteca Python que oferece ferramentas SQL e mapeamento objeto-relacional (Object-Relational Mapping — ORM).
- **Psycopg:** driver que permite a comunicação entre Python e PostgreSQL.
- **Alembic:** ferramenta de migrações (Database Migrations) que gere alterações do esquema da base de dados.
- **FastAPI:** framework da API; ainda não ligámos um endpoint ao modelo `User` neste dia.

### 2.1 Engine, Connection e Session

| Componente | Responsabilidade | Observação |
|---|---|---|
| `Engine` | Coordena o acesso à base de dados e, normalmente, gere um conjunto de ligações (Connection Pool) | Criá-lo não implica abrir imediatamente uma ligação física. |
| `Connection` | Representa uma ligação utilizada para executar instruções SQL | Pode ser obtida com `engine.connect()`. |
| `Session` | Gere objetos ORM e transações como unidade de trabalho (Unit of Work) | É criada a partir de `sessionmaker`. |

**Importante:** um *Connection Pool* não é um *Thread Pool*. O primeiro reutiliza ligações à base de dados; o segundo gere threads de execução.

## 3. Verificação do ambiente

Na raiz do projeto:

```bash
docker compose ps
docker ps
```

Resultados observados: serviço `db`, container `financetracker-db`, imagem `postgres:17`, estado `Up` e publicação da porta `127.0.0.1:5432->5432/tcp`.

| Comando/argumento | Explicação |
|---|---|
| `docker` | Cliente de linha de comandos do Docker. |
| `compose` | Usa a definição de serviços do `compose.yaml`. |
| `ps` em `docker compose ps` | Lista os containers associados ao projeto Compose. |
| `ps` em `docker ps` | Lista os containers Docker em execução, independentemente do projeto Compose. |

Para iniciar o serviço, quando necessário:

```bash
docker compose up -d db
```

- `up`: cria/inicia os serviços definidos no Compose.
- `-d`: execução em segundo plano (Detached Mode).
- `db`: nome do serviço no `compose.yaml`.

Dentro de `backend/`, com o ambiente virtual ativo:

```bash
python -c "import sqlalchemy; print(sqlalchemy.__version__)"
```

Resultado observado: `2.1.8`.

- `python`: interpretador do ambiente virtual ativo.
- `-c`: executa a instrução Python fornecida como argumento.
- `import sqlalchemy`: importa a biblioteca.
- `sqlalchemy.__version__`: obtém a versão instalada.
- `print(...)`: apresenta o resultado no terminal.

## 4. Ligação Python → PostgreSQL

Ficheiro criado: `backend/app/database.py`.

```python
import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://financetracker:dev_password@127.0.0.1:5432/financetracker",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


def check_database_connection() -> bool:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return True
```

Este é o código de referência resultante das etapas do dia; a organização exata das linhas no ficheiro local pode variar.

### 4.1 Elementos da URL de ligação

```text
postgresql+psycopg://financetracker:dev_password@127.0.0.1:5432/financetracker
```

| Parte | Significado |
|---|---|
| `postgresql` | Dialeto de base de dados utilizado pelo SQLAlchemy. |
| `+psycopg` | Driver Python utilizado. |
| `financetracker` antes de `:` | Utilizador da base de dados. |
| `dev_password` | Palavra-passe **apenas de desenvolvimento local**. |
| `127.0.0.1` | Host acessível a partir da máquina Ubuntu. |
| `5432` | Porta PostgreSQL publicada pelo container. |
| `/financetracker` | Nome da base de dados. |

A URL acima funciona quando o backend é executado diretamente no Ubuntu e a porta do PostgreSQL é publicada no host. **Se o backend passar a correr noutro container Compose**, o host será normalmente `db`, e não `127.0.0.1`.

### 4.2 Funções e parâmetros

- `os.getenv("DATABASE_URL", valor_padrao)`: lê uma variável de ambiente; utiliza o valor padrão quando ela não está definida.
- `create_engine(DATABASE_URL, pool_pre_ping=True)`: cria um `Engine`; `pool_pre_ping=True` verifica a validade das ligações antes de as reutilizar.
- `sessionmaker(bind=engine, ...)`: configura uma fábrica de sessões associada ao `Engine`.
- `autoflush=False`: desativa o *flush* automático antes de certas operações; `commit()` continua a efetuar o *flush* necessário.
- `expire_on_commit=False`: mantém os atributos carregados acessíveis depois do `commit()`, sem os expirar automaticamente.
- `with engine.connect() as connection`: abre uma ligação para o bloco e liberta-a no final.
- `text("SELECT 1")`: representa uma instrução SQL textual executável.

### 4.3 Teste de ligação

```bash
python -c "from app.database import check_database_connection; print(check_database_connection())"
```

**Resultado observado:** `True`.

Isso confirma que a aplicação conseguiu executar uma consulta no PostgreSQL, não apenas importar as bibliotecas.

## 5. Primeiro modelo ORM: User

Estrutura criada:

```text
backend/
└── app/
    ├── database.py
    ├── main.py
    └── models/
        ├── __init__.py
        └── user.py
```

Comandos utilizados:

```bash
mkdir -p app/models
touch app/models/__init__.py
touch app/models/user.py
```

- `mkdir`: cria um diretório.
- `-p`: cria diretórios intermédios se necessário e não falha se o diretório já existir.
- `touch`: cria um ficheiro vazio se ainda não existir ou atualiza a sua data de modificação.
- `__init__.py`: identifica explicitamente `models` como pacote Python.

Código do modelo `app/models/user.py`:

```python
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
```

| Elemento | Significado |
|---|---|
| `class User(Base)` | Herança (Inheritance): a classe é um modelo declarativo SQLAlchemy. |
| `__tablename__ = "users"` | Nome da tabela. |
| `Mapped[int]`, `Mapped[str]` | Anotações de tipo para atributos mapeados. |
| `mapped_column(...)` | Define as características de uma coluna. |
| `Integer` | Tipo inteiro SQL. |
| `String(100)` / `String(255)` | Texto com limite de comprimento. |
| `primary_key=True` | Define a chave primária (Primary Key). |
| `unique=True` | Exige valores únicos, neste caso para o email. |
| `nullable=False` | Proíbe `NULL` na coluna. |
| `hashed_password` | Campo destinado a guardar um hash de palavra-passe, **não** uma palavra-passe em texto simples. |

`Base.metadata` reúne as definições de tabelas dos modelos importados. **Definir a classe não cria automaticamente a tabela na base de dados.**

### 5.1 Testes do modelo

```bash
python -c "from app.models.user import User; print(User.__tablename__)"
python -c "from app.models.user import User; print(User.__table__.columns.keys())"
```

Resultados observados **antes de adicionar `hashed_password`**:

```text
users
['id', 'name', 'email']
```

Posteriormente foi acrescentado `hashed_password` **antes da primeira migração**, que já contém as quatro colunas.

## 6. Alembic: criação e configuração

### 6.1 Inicialização

```bash
alembic init alembic
```

- Primeiro `alembic`: executável da ferramenta.
- `init`: inicializa a estrutura de migrações.
- Segundo `alembic`: nome do diretório de configuração/migrações.

Ficheiros/diretórios principais:

```text
backend/
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
└── app/
```

### 6.2 Alterações em `alembic/env.py`

```python
from app.database import Base, DATABASE_URL
from app.models.user import User

config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

target_metadata = Base.metadata
```

Estas linhas são inseridas **no contexto do ficheiro `env.py` gerado**, mantendo os outros imports e as funções `run_migrations_offline()` e `run_migrations_online()`.

- Importar `User` faz com que o seu mapeamento seja registado nos metadados de `Base`.
- `target_metadata = Base.metadata` permite que a geração automática compare modelos e esquema da base de dados.
- `config.set_main_option("sqlalchemy.url", DATABASE_URL)` define a URL de ligação utilizada pelo Alembic.
- *Online migrations* utilizam uma ligação real; *offline migrations* podem gerar SQL sem ligação ativa, dependendo da configuração.

### 6.3 Gerar a primeira revisão

```bash
alembic revision --autogenerate -m "create users table"
```

| Parte | Função |
|---|---|
| `revision` | Cria uma revisão de migração. |
| `--autogenerate` | Compara os metadados ORM com o esquema atual da base de dados. |
| `-m` | Define a mensagem descritiva. |
| `"create users table"` | Mensagem associada à revisão. |

Saída observada: `Detected added table 'users'` e criação de:

```text
alembic/versions/35aa64b7c1c5_create_users_table.py
```

O ficheiro gerado define:

```python
def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )


def downgrade() -> None:
    op.drop_table("users")
```

- `upgrade()`: aplica a alteração do esquema.
- `downgrade()`: reverte a alteração. **Aqui elimina a tabela `users` e os seus dados!**
- `revision = '35aa64b7c1c5'`: identificador da migração.
- `down_revision = None`: primeira revisão, sem antecessora.

**Boa prática:** rever sempre a migração gerada; `--autogenerate` não garante que todas as alterações propostas sejam seguras ou desejadas.

### 6.4 Aplicar e verificar a migração

```bash
alembic upgrade head
alembic current
```

- `upgrade`: aplica migrações pendentes.
- `head`: revisão mais recente na sequência atual.
- `current`: mostra a revisão aplicada na base de dados.

Resultado observado:

```text
35aa64b7c1c5 (head)
```

## 7. Verificação no PostgreSQL com psql

A partir da raiz do projeto:

```bash
docker compose exec db psql -U financetracker -d financetracker
```

| Parte | Explicação |
|---|---|
| `docker compose exec` | Executa um comando dentro de um container de serviço em execução. |
| `db` | Serviço PostgreSQL no `compose.yaml`. |
| `psql` | Cliente de linha de comandos do PostgreSQL. |
| `-U financetracker` | Utilizador PostgreSQL. |
| `-d financetracker` | Base de dados à qual ligar. |

Comandos no `psql`:

```sql
\dt
\d users
SELECT * FROM alembic_version;
```

- `\dt`: lista tabelas.
- `\d users`: descreve as colunas, índices e restrições da tabela `users`.
- `SELECT * FROM alembic_version;`: consulta a revisão aplicada e guardada pelo Alembic.
- `;`: termina uma instrução SQL (não é necessário nos meta-comandos `\dt` e `\d`).

Resultado confirmado para a revisão: `35aa64b7c1c5`.

Estrutura observada de `users`:

| Coluna | Tipo PostgreSQL | Restrição |
|---|---|---|
| `id` | `integer` | `NOT NULL`, chave primária, valor por sequência `users_id_seq` |
| `name` | `character varying(100)` | `NOT NULL` |
| `email` | `character varying(255)` | `NOT NULL`, `UNIQUE` |
| `hashed_password` | `character varying(255)` | `NOT NULL` |

`nextval('users_id_seq'::regclass)` é o valor por defeito da coluna `id`: a sequência fornece novos identificadores. Não se deve assumir que IDs serão sempre consecutivos, pois sequências podem ter lacunas.

## 8. Inserção e consulta com Session

Ficheiro criado: `backend/scripts/test_database.py`.

```bash
mkdir -p scripts
touch scripts/test_database.py
```

Exemplo representativo do script de teste:

```python
from app.database import SessionLocal
from app.models.user import User


def main():
    with SessionLocal() as session:
        user = User(
            name="Test User",
            email="test@exemple.com",
            hashed_password="NOT_A_REAL_PASSWORD_HASH",
        )

        session.add(user)
        session.commit()

        print(f"User created with id: {user.id}")

        saved_user = session.get(User, user.id)
        if saved_user is not None:
            print(f"Name: {saved_user.name}")
            print(f"Email: {saved_user.email}")


if __name__ == "__main__":
    main()
```

> O valor `NOT_A_REAL_PASSWORD_HASH` é **fictício e não é um hash válido**. O teste não implementa autenticação. Não usar este valor para contas reais.

Executado a partir de `backend/`:

```bash
python -m scripts.test_database
```

- `python`: interpretador Python.
- `-m`: executa um módulo, usando o contexto de importação do projeto.
- `scripts.test_database`: caminho do módulo Python correspondente a `scripts/test_database.py`.

Resultado observado:

```text
User created with id: 1
Name: Test User
Email: test@exemple.com
```

### 8.1 Métodos de Session

| Operação | Efeito |
|---|---|
| `SessionLocal()` | Cria uma nova sessão a partir da fábrica. |
| `with ... as session` | Garante o encerramento da sessão ao sair do bloco. Não confirma automaticamente a transação. |
| `session.add(user)` | Coloca o objeto sob gestão da sessão como pendente (Pending). |
| `session.flush()` | Envia SQL pendente à base de dados dentro da transação, sem a confirmar. Pode acontecer automaticamente em determinadas operações. |
| `session.commit()` | Faz o flush necessário e confirma a transação. |
| `session.rollback()` | Reverte a transação ainda não confirmada. |
| `session.get(User, id)` | Obtém um registo pela chave primária, podendo reutilizar o objeto já presente na sessão. |

**Atenção:** `session.add()` não equivale a `INSERT` confirmado. Um `INSERT` pode ser emitido durante o *flush*, mas a persistência definitiva depende do `commit()`.

### 8.2 Ciclo de vida de um objeto ORM

```mermaid
stateDiagram-v2
    [*] --> Transient: User(...)
    Transient --> Pending: session.add(user)
    Pending --> Persistent: flush / INSERT
    Persistent --> Detached: session.close() / expunge()
    Persistent --> Deleted: session.delete() + flush
    Deleted --> Detached: commit
```

- **Transient:** objeto Python ainda não associado a uma sessão.
- **Pending:** objeto adicionado à sessão, à espera de inserção.
- **Persistent:** objeto associado à sessão e representado na base de dados; o `flush` realiza a transição, mesmo antes do `commit`.
- **Detached:** objeto que já não está associado a uma sessão.
- **Deleted:** objeto marcado para eliminação e cujo `DELETE` foi enviado durante o *flush*.

O diagrama simplifica alguns casos, como `rollback()`, que pode devolver um objeto recém-inserido ao estado *Transient*.

## 9. Confirmação independente dos dados

No `psql`, foi executado:

```sql
SELECT id, name, email FROM users;
```

Resultado **observado**:

```text
 id |   name    |      email
----+-----------+------------------
  1 | Test User | test@exemple.com
(1 row)
```

Este teste comprova que os dados continuaram disponíveis no PostgreSQL após o fim do script Python e o encerramento da sessão.

## 10. Fluxo completo do Dia 3

```mermaid
flowchart TD
    A[Docker Compose: PostgreSQL ativo] --> B[SQLAlchemy: Engine e SessionLocal]
    B --> C[Teste SELECT 1: True]
    C --> D[Modelo User com 4 colunas]
    D --> E[Alembic revision --autogenerate]
    E --> F[Revisão humana de upgrade/downgrade]
    F --> G[Alembic upgrade head]
    G --> H[users e alembic_version no PostgreSQL]
    H --> I[Session.add + Session.commit]
    I --> J[SELECT no psql confirma o registo]
```

## 11. Cuidados, limites e erros comuns

1. **Não confundir modelo com tabela:** definir `class User(Base)` não altera o PostgreSQL; é preciso uma migração ou outro mecanismo explícito de criação de esquema.
2. **Não confundir `revision` com `upgrade`:** `revision --autogenerate` gera um ficheiro; `upgrade head` aplica as alterações.
3. **Não confundir `add`, `flush` e `commit`:** cada um tem papel diferente no ciclo de persistência.
4. **Não executar o script de teste repetidamente com o mesmo email:** a restrição `UNIQUE` provoca `IntegrityError` na segunda tentativa; uma falha exige `rollback()` antes de reutilizar a sessão.
5. **Não armazenar palavras-passe reais em texto simples:** a coluna `hashed_password` exige um hash gerado por um algoritmo apropriado, como Argon2, que ainda não foi implementado.
6. **Não publicar credenciais:** mover `DATABASE_URL` para variável de ambiente/`.env` ignorado pelo Git antes de partilhar o projeto. A senha de exemplo só serve para ambiente local.
7. **Não executar `downgrade()` inadvertidamente:** a migração atual elimina a tabela `users` e todos os seus dados.
8. **Não assumir que `localhost` funciona entre containers:** em Docker Compose, o backend containerizado deverá comunicar com o serviço `db` pela rede interna.
9. **Não confundir `Connection Pool` com `Thread Pool`:** são mecanismos distintos.
10. **Não considerar um teste de importação como teste de conectividade:** `import sqlalchemy` confirma a biblioteca; `SELECT 1` via `Engine` confirma o acesso à base de dados.

## 12. Exercícios de revisão

1. Qual é a diferença entre PostgreSQL, SQLAlchemy e Psycopg?
2. O que faz `Base.metadata` e por que o Alembic precisa dele?
3. Qual é a diferença entre `alembic revision --autogenerate` e `alembic upgrade head`?
4. Qual é a diferença entre `session.add()`, `session.flush()` e `session.commit()`?
5. Por que `session.get(User, 1)` não precisa de uma instrução SQL `SELECT` escrita manualmente?
6. O que acontece ao executar o script duas vezes com o mesmo email?
7. O que significa a revisão `35aa64b7c1c5 (head)`?
8. Por que uma coluna chamada `hashed_password` não garante, por si só, que a palavra-passe esteja protegida?

## 13. Próximos passos

- Tratar erros de integridade e transações (`IntegrityError`, `rollback`).
- Definir esquemas de entrada/saída com Pydantic.
- Implementar hashing real de palavras-passe e registo de utilizadores.
- Criar endpoints FastAPI que utilizem sessões de base de dados por pedido.
- Evoluir para login, autenticação e, posteriormente, gestão de transações financeiras.

---

**Conclusão:** no Dia 3, o FinanceTracker passou de um backend com PostgreSQL configurado para um backend capaz de **ligar-se à base de dados, definir e migrar o esquema, inserir dados e consultá-los através do SQLAlchemy ORM**.
