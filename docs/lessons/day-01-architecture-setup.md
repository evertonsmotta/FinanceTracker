# FinanceTracker — Dia 1: Arquitetura e preparação do ambiente

> **Duração prevista:** 45–60 minutos  
> **Objetivo:** compreender a arquitetura Full-Stack, preparar o repositório e executar o primeiro endpoint FastAPI.  
> **Método:** compreender → implementar → testar → explicar. Não copiar uma solução completa antes de tentar.

## Sumário

1. Compreender a arquitetura
2. Relacionar os conceitos com C++
3. Criar o repositório
4. Preparar o ambiente virtual Python
5. Criar o primeiro endpoint
6. Executar e testar a API
7. Verificação de aprendizagem
8. Checklist de conclusão do Dia 1
9. Entrega e revisão de código

## 1. Compreender a arquitetura

O FinanceTracker é uma aplicação web para gerir receitas e despesas pessoais. A arquitetura inicial separa três responsabilidades:

```text
[Frontend: Angular + TypeScript]  http://localhost:4200
             |
             | HTTP / JSON
             v
[Backend: Python + FastAPI]      http://localhost:8000
             |
             | SQLAlchemy / SQL
             v
[Base de dados: PostgreSQL]      localhost:5432 (desenvolvimento)
```

- **Frontend:** interface, formulários, navegação e apresentação dos dados.
- **Backend:** rotas HTTP, validação, autenticação, autorização e regras de negócio.
- **Base de dados:** armazenamento persistente de utilizadores e transações.
- **Docker Compose:** numa etapa posterior, permitirá executar e coordenar os serviços em containers.

**Regra importante:** o frontend não deve aceder diretamente à base de dados. O backend controla o acesso e as permissões.

### Exemplo de fluxo: login

1. O utilizador introduz e-mail e palavra-passe num formulário Angular.
2. O Angular envia um pedido `POST` para o FastAPI.
3. O FastAPI valida os dados recebidos.
4. O backend consulta o utilizador no PostgreSQL.
5. O backend verifica a palavra-passe e estabelece a autenticação.
6. O Angular recebe o resultado e atualiza a interface.

> **Nota:** este fluxo é conceptual. A autenticação não será implementada no Dia 1.

## 2. Relacionar os conceitos com C++

| Conceito | C++ | Python / FastAPI |
|---|---|---|
| Função | `int sum(int a, int b)` | `def sum(a: int, b: int) -> int:` |
| Estruturas de dados | `struct` / `class` | `class`, `dataclass`, Pydantic |
| Organização de código | Headers e ficheiros `.cpp` | Módulos e packages `.py` |
| Dependências | CMake e bibliotecas | `pip` e `pyproject.toml` |
| Servidor HTTP | Biblioteca/framework externo | FastAPI + Uvicorn |

As anotações de tipo (*type hints*) em Python não impõem, por si só, verificação obrigatória em tempo de execução. O FastAPI usa anotações e Pydantic para validar dados recebidos.

## 3. Criar o repositório (≈ 10 minutos)

No terminal Ubuntu:

```bash
mkdir finance-tracker
cd finance-tracker

git init
mkdir backend frontend docs
```

Verifica a estrutura:

```bash
tree -L 2
```

Resultado esperado:

```text
finance-tracker/
├── backend/
├── docs/
└── frontend/
```

### Porquê um monorepo?

Um *monorepo* (repositório único) reúne frontend, backend e infraestrutura no mesmo repositório Git. Para este projeto de aprendizagem, simplifica a organização e a evolução conjunta dos componentes.

## 4. Preparar o ambiente virtual Python (≈ 10 minutos)

Entra no backend e verifica a versão do Python:

```bash
cd backend
python3 --version
```

**Recomendação:** Python 3.11 ou superior. Se o Ubuntu 22.04 tiver Python 3.10, é possível adaptar o ambiente sem alterar o Python do sistema.

Cria e ativa um ambiente virtual (*virtual environment*):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

O prompt deverá começar com `(.venv)`.

Instala as dependências iniciais:

```bash
python -m pip install fastapi "uvicorn[standard]"
```

**Conceitos:**

- `.venv`: isola as dependências Python deste projeto.
- `FastAPI`: framework para desenvolver APIs HTTP.
- `Uvicorn`: servidor ASGI (*Asynchronous Server Gateway Interface*) que executa a aplicação.

**Boa prática:** adiciona `.venv/` ao `.gitignore` antes de criar o primeiro commit. Nunca incluas o ambiente virtual no repositório.

## 5. Criar o primeiro endpoint (≈ 15 minutos)

Cria os ficheiros:

```bash
mkdir -p app
touch app/__init__.py app/main.py
```

Estrutura esperada:

```text
backend/
├── .venv/
└── app/
    ├── __init__.py
    └── main.py
```

### Três elementos fundamentais

**1. Importação:**

```python
from fastapi import FastAPI
```

**2. Instância da aplicação:**

```python
app = FastAPI()
```

**3. Decorador de rota:**

```python
@app.get("/health")
```

Um *decorator* (decorador) associa uma função Python ao tratamento de pedidos HTTP numa rota específica.

### Desafio prático — implementa sem copiar uma solução completa

No ficheiro `app/main.py`, implementa uma função com os seguintes requisitos:

- **Método HTTP:** `GET`
- **Caminho:** `/health`
- **Nome da função:** `health_check`
- **Resposta JSON:** `{"status": "ok"}`

**Dica:** uma função Python pode devolver `return {"status": "ok"}`. O FastAPI converte o dicionário para JSON automaticamente.

## 6. Executar e testar a API (≈ 10 minutos)

No diretório `backend`, com o ambiente virtual ativo:

```bash
uvicorn app.main:app --reload
```

| Parte do comando | Significado |
|---|---|
| `uvicorn` | Inicia o servidor ASGI |
| `app.main` | Importa o módulo `app/main.py` |
| `:app` | Procura a instância FastAPI chamada `app` |
| `--reload` | Reinicia automaticamente o servidor após alterações no código, durante o desenvolvimento |

Abre no navegador:

- Endpoint: http://127.0.0.1:8000/health
- Documentação interativa (Swagger UI): http://127.0.0.1:8000/docs

Resposta esperada de `/health`:

```json
{
  "status": "ok"
}
```

No Swagger UI, encontra a operação `GET /health` e testa-a com **Try it out**.

## 7. Verificação de aprendizagem

Responde antes de consultar as soluções:

1. Qual é a principal responsabilidade do FastAPI?
   - A. Renderizar os componentes Angular.
   - (B). Processar pedidos HTTP e aplicar regras de negócio.
   - C. Armazenar os dados permanentemente.
2. O que significa `@app.get("/health")`?
   - A. Criar uma tabela SQL.
   - (B). Associar uma função a uma rota HTTP GET.
   - C. Executar uma função automaticamente a cada segundo.
3. Para que serve `--reload` no Uvicorn?
   - A. Reinstalar dependências.
   - (B). Reiniciar o servidor quando o código muda.
   - C. Recarregar o PostgreSQL.

<details>
<summary>Ver respostas e explicações</summary>

1. **B.** O FastAPI trata pedidos HTTP, valida dados e executa lógica do backend; a persistência cabe à base de dados.
2. **B.** O decorador regista a função como responsável pelos pedidos GET na rota `/health`.
3. **B.** `--reload` facilita o desenvolvimento ao reiniciar o servidor quando o código é alterado.

</details>

## 8. Checklist de conclusão do Dia 1

- [DONE] Repositório Git inicializado.
- [DONE] Diretórios `backend/`, `frontend/` e `docs/` criados.
- [DONE] Ambiente virtual Python criado e ativado.
- [DONE] FastAPI e Uvicorn instalados.
- [DONE] Endpoint `GET /health` implementado.
- [DONE] Resposta validada no navegador.
- [DONE] Endpoint testado no Swagger UI.
- [DONE] `.venv/` incluído no `.gitignore`.

## 9. Entrega e revisão de código

Ao concluir, partilha:

1. O conteúdo de `backend/app/main.py`.
2. A resposta obtida em `GET /health`.
3. Eventuais erros ou dúvidas.

Faremos uma pequena revisão de código (*code review*) antes de avançar.

### Próxima aula — Dia 2

**PostgreSQL, SQLAlchemy, modelos de dados e primeira migração com Alembic.** O objetivo será começar a persistir informação e compreender a relação entre os modelos Python e as tabelas SQL.

---

**Princípio do projeto:** avançar gradualmente, compreendendo cada camada antes de integrá-la com as restantes.
