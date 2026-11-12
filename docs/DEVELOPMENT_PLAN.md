# FinanceTracker — Plano Inicial de Desenvolvimento e Estudos

> **Objetivo:** construir uma aplicação simples de controlo financeiro pessoal para praticar diariamente desenvolvimento *full-stack* com Angular, TypeScript, Python/FastAPI, PostgreSQL e Docker.
>
> **Ritmo de estudo:** 30–60 minutos por dia. **Abordagem:** compreender conceitos, implementar incrementalmente, testar e repetir sem copiar soluções prontas.

## 1. O projeto: FinanceTracker

O **FinanceTracker** será uma aplicação web para gerir receitas e despesas e acompanhar o saldo pessoal. O projeto deve manter-se pequeno, mas incluir desde o início registo de utilizador, login e logout.

### Funcionalidades da primeira versão (MVP)

- Registo de utilizador com nome, e-mail e palavra-passe.
- Login e logout com autenticação segura.
- Página privada acessível apenas a utilizadores autenticados.
- Criação, listagem, edição e eliminação de receitas e despesas (*CRUD*).
- Cálculo do saldo atual e resumo mensal simples.
- Isolamento dos dados: cada utilizador só pode consultar e modificar as suas próprias transações.

**Fora do âmbito inicial:** gráficos avançados, orçamentos, notificações, exportações, recuperação de palavra-passe e integrações bancárias.

## 2. Stack tecnológica recomendada

| Camada | Tecnologia | Conceitos a praticar |
|---|---|---|
| Frontend | Angular + TypeScript + SCSS | Componentes *standalone*, serviços, rotas, formulários reativos, RxJS, HttpClient |
| Backend | Python + FastAPI + Uvicorn | APIs REST, rotas, dependências, validação com Pydantic |
| ORM | SQLAlchemy | Modelos, relações e consultas |
| Migrações | Alembic | Versionamento do esquema da base de dados |
| Base de dados | PostgreSQL | SQL, chaves primárias e estrangeiras, relações, transações |
| Autenticação | Hash Argon2 + sessão/JWT | Identidade, autorização, cookies e segurança |
| Infraestrutura | Docker + Docker Compose | Imagens, containers, volumes e redes |
| Testes | Pytest | Testes unitários e de integração |
| Versionamento | Git | Commits, branches e revisões |

### Arquitetura

```text
Navegador
   |
   v
Angular (frontend, porta 4200)
   | HTTP / JSON
   v
FastAPI (backend, porta 8000)
   | SQLAlchemy
   v
PostgreSQL (porta 5432, ambiente local)

Docker Compose: orquestração dos serviços numa fase posterior.
```

**Responsabilidades:** o frontend apresenta dados e recolhe entradas; o backend valida, autentica e aplica regras de negócio; o PostgreSQL persiste os dados. O frontend nunca deve comunicar diretamente com a base de dados.

## 3. Modelo de dados inicial

### Tabela `users`

| Campo | Tipo | Observação |
|---|---|---|
| `id` | UUID | Chave primária (PK) |
| `name` | VARCHAR | Nome do utilizador |
| `email` | VARCHAR | Único; utilizado no login |
| `password_hash` | VARCHAR | Nunca guardar passwords em texto simples |
| `created_at` | TIMESTAMP | Data de criação |

### Tabela `transactions`

| Campo | Tipo | Observação |
|---|---|---|
| `id` | UUID | Chave primária (PK) |
| `user_id` | UUID | Chave estrangeira (FK) para `users.id` |
| `description` | VARCHAR | Descrição |
| `amount` | NUMERIC(12,2) | Valor monetário |
| `type` | VARCHAR/ENUM | `income` ou `expense` |
| `category` | VARCHAR | Categoria |
| `date` | DATE | Data da transação |
| `created_at` | TIMESTAMP | Data de criação |

**Relação:** um utilizador pode ter várias transações (*one-to-many*). Usar `Decimal` em Python e `NUMERIC` em PostgreSQL para valores monetários, evitando `float`.

## 4. Endpoints da API

| Método | Endpoint | Objetivo | Autenticação |
|---|---|---|---|
| `POST` | `/auth/register` | Criar conta | Não |
| `POST` | `/auth/login` | Autenticar | Não |
| `POST` | `/auth/logout` | Terminar sessão | Sim |
| `GET` | `/users/me` | Consultar perfil | Sim |
| `GET` | `/transactions` | Listar transações próprias | Sim |
| `POST` | `/transactions` | Criar transação | Sim |
| `PUT` | `/transactions/{id}` | Atualizar transação própria | Sim |
| `DELETE` | `/transactions/{id}` | Eliminar transação própria | Sim |
| `GET` | `/dashboard/summary` | Consultar resumo financeiro | Sim |
| `GET` | `/health` | Verificar estado básico da API | Não |

**Segurança:** utilizar hash de passwords com Argon2. Para autenticação via cookie, configurar `HttpOnly`, `Secure` em produção e `SameSite` adequado; considerar proteção CSRF. Se forem utilizados JWT, definir uma estratégia efetiva de expiração/revogação: remover um token do frontend não invalida automaticamente um JWT ainda válido. Cada operação de transação deve verificar a propriedade do recurso no backend.

A documentação interativa do FastAPI ficará normalmente disponível em `/docs`.

## 5. Estrutura sugerida do repositório

```text
finance-tracker/
├── frontend/
│   ├── src/
│   ├── angular.json
│   ├── package.json
│   └── Dockerfile
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── tests/
│   ├── alembic/
│   ├── pyproject.toml
│   └── Dockerfile
├── docs/
├── compose.yaml
├── .env.example
├── .gitignore
└── README.md
```

Usar um *monorepo* para manter frontend, backend e infraestrutura num único repositório. Esta é a **estrutura-alvo**: os diretórios serão criados gradualmente, não todos no primeiro dia.

## 6. Plano de desenvolvimento inicial (5 sessões)

O calendário é indicativo e deve ser ajustado à disponibilidade e ao ritmo de aprendizagem. Com 30–60 minutos diários, algumas sessões poderão precisar de ser divididas.

### Dia 1 — Ambiente e primeiro endpoint
- [ ] Inicializar Git e criar `backend/`, `frontend/` e `docs/`.
- [ ] Confirmar a versão de Python e criar `.venv` no backend.
    - Comando: `python3 -m venv .venv` e `source .venv/bin/activate`.
- [ ] Instalar FastAPI e Uvicorn.
    - Comando: `python -m pip install fastapi "uvicorn[standard]"`.
- [ ] Implementar `GET /health` com resposta `{"status": "ok"}`.
- [ ] Executar a API e testar `/health` e `/docs`.

### Dia 2 — Backend e base de dados
- [ ] Preparar PostgreSQL (preferencialmente com Docker Compose).
- [ ] Configurar SQLAlchemy e ligação à base de dados.
- [ ] Definir modelos `User` e `Transaction`.
- [ ] Introduzir Alembic e criar a primeira migração.

### Dia 3 — Autenticação
- [ ] Implementar registo de utilizador com validação.
- [ ] Guardar password com hash seguro.
- [ ] Implementar login e mecanismo de sessão.
- [ ] Implementar logout e proteção de endpoints.
- [ ] Criar testes básicos com Pytest.

### Dia 4 — Frontend Angular
- [ ] Criar a aplicação Angular.
- [ ] Implementar páginas de registo e login.
- [ ] Utilizar *Reactive Forms* para validação.
- [ ] Criar `AuthService` e proteção de rotas.

### Dia 5 — Integração e revisão
- [ ] Integrar Angular com FastAPI através de `HttpClient`.
- [ ] Implementar criação e listagem de transações.
- [ ] Testar o fluxo completo: registo → login → transação → logout.
- [ ] Rever SQL, Docker, HTTP, autenticação e conceitos aprendidos.

**Nota de âmbito:** estas são metas progressivas, não um compromisso de concluir todas as funcionalidades em cinco horas. Priorizar um fluxo pequeno e compreendido, mesmo que o desenvolvimento demore mais dias.

## 7. Método de estudo e prática diária

Para cada funcionalidade, seguir cinco passos:

1. **Conceito:** compreender o problema, os componentes e a terminologia.
2. **Implementação:** escrever o código com orientação, evitando copiar soluções completas.
3. **Fluxo:** acompanhar os dados do Angular ao FastAPI, à base de dados e de volta.
4. **Testes:** verificar casos de sucesso, erros e autorização.
5. **Repetição:** reconstruir no dia seguinte uma pequena parte sem consultar o código.

### Exemplo de fluxo de login

```text
Angular: formulário de login
    ↓ POST /auth/login (HTTP/JSON)
FastAPI: validação com Pydantic
    ↓
SQLAlchemy: consulta do utilizador
    ↓
PostgreSQL: dados do utilizador
    ↓
FastAPI: verificação do hash e criação da sessão
    ↓ Resposta HTTP / cookie de sessão
Angular: atualiza o estado de autenticação e navega para o dashboard
```

**Perguntas para revisão:**
- Qual é a diferença entre frontend, backend e base de dados?
- O que é uma API REST e para que serve um endpoint?
- Qual é a diferença entre `GET` e `POST`?
- Como é feita a validação de dados no FastAPI?
- Por que razão a password deve ser armazenada como hash?
- Como se garante que um utilizador não acede às transações de outro?
- O que fazem SQLAlchemy, Alembic e Docker Compose?

## 8. Primeira aula prática — instruções resumidas

### Criar o repositório

```bash
mkdir finance-tracker
cd finance-tracker
git init
mkdir backend frontend docs
```

### Preparar o backend

```bash
cd backend
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install fastapi "uvicorn[standard]"
mkdir -p app
touch app/__init__.py app/main.py
```

**Desafio:** implementar em `app/main.py` um endpoint `GET /health` com uma função chamada `health_check` que devolva `{"status": "ok"}`. Utilizar `FastAPI()`, o decorador `@app.get(...)` e um dicionário Python como resposta.

### Executar e verificar

```bash
uvicorn app.main:app --reload
```

Abrir:
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

**Conceitos:** `uvicorn` inicia o servidor ASGI; `app.main:app` identifica o módulo e a instância FastAPI; `--reload` reinicia o servidor após alterações durante o desenvolvimento.

### Critério de conclusão

O Dia 1 estará concluído quando o endpoint responder corretamente e for possível explicares o caminho de um pedido HTTP até à função Python.

## 9. Próximas evoluções (após o MVP)

- Dashboard com gráficos simples.
- Filtros por categoria e período.
- Orçamentos mensais.
- Exportação CSV.
- Recuperação de palavra-passe.
- Testes end-to-end com Cypress.
- Pipeline CI/CD.
- Deploy num ambiente de demonstração.

---

**Princípio do projeto:** desenvolver pouco de cada vez, compreender as decisões e manter a aplicação funcional ao longo do percurso.
