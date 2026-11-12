# FinanceTracker — Gunicorn vs. Uvicorn

> Nota técnica de aprendizagem | Backend Python / FastAPI

## Decisão do projeto

**O FinanceTracker começará com Uvicorn diretamente**, durante o desenvolvimento local. A utilização de Gunicorn com workers ASGI poderá ser estudada posteriormente, quando abordarmos processos, concorrência, Docker e deployment. Gunicorn **não é obrigatório** para colocar FastAPI em produção.

## 1. Por que Uvicorn?

FastAPI é uma framework baseada em **ASGI (Asynchronous Server Gateway Interface)**. Uvicorn é um servidor ASGI que executa a aplicação diretamente e suporta funcionalidades como `async/await` e WebSockets.

No diretório `backend/`, com o ambiente virtual ativado:

```bash
python -m pip install fastapi "uvicorn[standard]"
uvicorn app.main:app --reload
```

- `app.main`: módulo Python `app/main.py`.
- `:app`: objeto FastAPI criado nesse módulo.
- `--reload`: reinicia o servidor ao detetar alterações no código; **apenas para desenvolvimento**.

A documentação interativa estará normalmente em `http://127.0.0.1:8000/docs`.

## 2. WSGI e ASGI

### WSGI — Web Server Gateway Interface

Interface tradicional entre servidores e aplicações Python, usada habitualmente por aplicações Flask. É essencialmente síncrona.

```text
Cliente → Gunicorn (worker WSGI) → Flask → Resposta HTTP
```

### ASGI — Asynchronous Server Gateway Interface

Interface que suporta aplicações assíncronas e protocolos como WebSockets.

```text
Cliente → Uvicorn (ASGI) → FastAPI → Resposta HTTP
```

**Importante:** ASGI não torna automaticamente cada pedido mais rápido. A vantagem da programação assíncrona surge sobretudo quando operações de entrada/saída (*I/O*) podem aguardar sem bloquear o ciclo de eventos (*event loop*).

## 3. Comparação

| Aspeto | Uvicorn | Gunicorn |
|---|---|---|
| Papel principal | Servidor ASGI | Servidor WSGI e gestor de processos/workers |
| FastAPI | Suporte direto | Necessita de worker ASGI compatível |
| Flask tradicional | Não diretamente, sem adaptação | Suporte WSGI direto |
| `async/await` | Suporte ASGI nativo | Depende do worker utilizado |
| WebSockets | Suportados | Com worker ASGI apropriado |
| Vários workers | Suportados | Suportados |
| Desenvolvimento com recarregamento | `--reload` | Possível, mas não necessário neste projeto |
| Produção | Possível | Possível com worker ASGI |

Uvicorn e Gunicorn **não são necessariamente alternativas mutuamente exclusivas**: podem trabalhar juntos.

## 4. Como funcionam juntos?

Gunicorn gere os processos de trabalho (*workers*). Cada worker ASGI executa a aplicação FastAPI, utilizando um servidor compatível com ASGI.

```text
                Gunicorn (processo principal)
                         |
              +----------+----------+
              |                     |
       Worker ASGI 1           Worker ASGI 2
              |                     |
           FastAPI               FastAPI
```

Uma configuração possível é instalar o pacote independente `uvicorn-worker`:

```bash
python -m pip install gunicorn uvicorn-worker

gunicorn app.main:app \
  -k uvicorn_worker.UvicornWorker \
  --workers 2 \
  --bind 0.0.0.0:8000
```

O caminho antigo `uvicorn.workers.UvicornWorker` está descontinuado; por isso, o exemplo utiliza `uvicorn_worker.UvicornWorker`.

**Segurança:** `0.0.0.0` expõe o serviço em todas as interfaces de rede disponíveis. Em desenvolvimento local, prefere `127.0.0.1` quando não precisas de acesso externo.

## 5. `def`, `async def` e bloqueio

### Exemplo que bloqueia o event loop

```python
import time
from fastapi import FastAPI

app = FastAPI()

@app.get("/blocking")
async def blocking():
    time.sleep(5)
    return {"status": "ok"}
```

Embora a função seja `async def`, `time.sleep(5)` bloqueia a thread que executa o event loop. Num único worker, outros pedidos assíncronos podem ficar à espera.

### Exemplo que permite concorrência durante a espera

```python
import asyncio

@app.get("/non-blocking")
async def non_blocking():
    await asyncio.sleep(5)
    return {"status": "ok"}
```

`await asyncio.sleep(5)` cede o controlo ao event loop. Três pedidos simultâneos que apenas aguardam cinco segundos podem terminar em aproximadamente cinco segundos, em vez de quinze, num cenário simplificado.

### E com `def`?

```python
@app.get("/sync")
def sync_endpoint():
    time.sleep(5)
    return {"status": "ok"}
```

No FastAPI, endpoints síncronos (`def`) são normalmente executados numa **thread pool**. Assim, vários pedidos podem decorrer concorrentemente em threads distintas, dentro dos limites do conjunto de threads. O `time.sleep` bloqueia a respetiva thread, mas não diretamente o event loop.

**Regra prática:**

- Utilizar `async def` com bibliotecas realmente assíncronas e operações `await`.
- Utilizar `def` quando a lógica depende de bibliotecas síncronas/bloqueantes, como uma sessão SQLAlchemy síncrona.
- Evitar chamadas bloqueantes dentro de `async def`.
- Para processamento intensivo de CPU, considerar processos ou workers dedicados, conforme a necessidade.

## 6. Plano de evolução no FinanceTracker

| Fase | Configuração | Objetivo |
|---|---|---|
| Inicial | `uvicorn app.main:app --reload` | Aprender FastAPI, rotas e debugging local |
| Integração | Uvicorn + PostgreSQL + Angular | Desenvolver e testar o fluxo full-stack |
| Docker | Serviço FastAPI com Uvicorn | Aprender containers, redes e volumes |
| Evolução | Comparar Uvicorn com múltiplos workers e Gunicorn + worker ASGI | Compreender concorrência e gestão de processos |
| Produção | Escolha conforme infraestrutura | Configurar workers, proxy, segurança e monitorização conforme o ambiente |

## 7. Pergunta de entrevista

**Pergunta:** «Por que escolher Uvicorn para FastAPI, se já trabalhaste com Gunicorn?»

**Resposta possível:**

> Tenho experiência profissional com Flask e Gunicorn. Para FastAPI, optei por começar com Uvicorn porque é um servidor ASGI e executa a aplicação diretamente, com suporte a funcionalidades assíncronas. Também sei que Gunicorn pode gerir múltiplos workers ASGI. A escolha depende das necessidades de desenvolvimento e deployment.

## 8. Exercícios de revisão

1. Explica a diferença entre WSGI e ASGI.
2. Qual é a responsabilidade do Uvicorn e qual é a do Gunicorn numa configuração conjunta?
3. Por que `async def` com `time.sleep(5)` pode prejudicar a concorrência?
4. Por que um endpoint `def` com uma operação bloqueante pode continuar a atender vários pedidos em paralelo, dentro dos limites da thread pool?
5. Por que não devemos utilizar `--reload` em produção?

---

**Decisão registada:** manter **Uvicorn** como servidor do FinanceTracker na fase inicial. Introduzir Gunicorn apenas como estudo comparativo ou quando houver uma necessidade concreta de deployment.
