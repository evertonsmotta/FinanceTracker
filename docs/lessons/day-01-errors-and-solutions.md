# FinanceTracker — Dia 1: Lições aprendidas com erros

> Guia de diagnóstico (*troubleshooting*) para consulta durante o desenvolvimento do FinanceTracker.

## Contexto

No Dia 1, configurámos um backend Python/FastAPI, executado com Uvicorn, e implementámos os endpoints `GET /`, `GET /health` e `GET /hello/{name}`. Este documento regista erros observados e erros de implementação identificados durante a revisão, distinguindo-os de hipóteses de diagnóstico.

## 1. `ModuleNotFoundError: No module named 'app'`

### Descrição do erro

Ao iniciar o Uvicorn, o Python não conseguiu importar o módulo `app`:

```text
ModuleNotFoundError: No module named 'app'
```

### Possíveis causas

- O comando `uvicorn app.main:app --reload` foi executado na raiz `FinanceTracker/`, em vez de `FinanceTracker/backend/`.
- A pasta `backend/app/` não existe, foi renomeada ou não contém `main.py`.
- A configuração do caminho de importação (*Python import path*) não inclui a pasta que contém `app`.
- Um comando ou configuração da IDE usa um diretório de trabalho (*working directory*) diferente do esperado.

**Nota:** a causa exata não foi confirmada apenas pelo excerto do traceback.

### Diagnóstico

```bash
pwd
ls -la app/
python -c "from app.main import app; print(app.title)"
```

Executar estes comandos a partir de `FinanceTracker/backend/`.

### Possíveis soluções

**Opção A — executar dentro do backend (recomendada neste projeto):**

```bash
cd ~/Documentos/github_repos/FinanceTracker/backend
source .venv/bin/activate
python -m uvicorn app.main:app --reload
```

**Opção B — executar a partir da raiz do repositório:**

```bash
cd ~/Documentos/github_repos/FinanceTracker
backend/.venv/bin/python -m uvicorn backend.app.main:app --reload
```

A opção B pressupõe a estrutura indicada e que o módulo pode ser importado dessa forma; se surgirem importações internas diferentes, devemos rever a configuração do projeto.

### Lição aprendida

`app.main:app` contém um **caminho de módulo** (`app.main`) e um **nome de objeto** (`app`). Não é um caminho absoluto do sistema de ficheiros.

---

## 2. `ERR_CONNECTION_REFUSED (-102)` no navegador

### Descrição do erro

Ao abrir `http://127.0.0.1:8000/`, o navegador apresentou:

```text
Failed to Load Page
ERR_CONNECTION_REFUSED (-102)
```

### Possíveis causas

- O servidor Uvicorn não iniciou devido ao erro de importação anterior.
- O servidor foi interrompido com `Ctrl+C`.
- A aplicação está a escutar noutra porta ou endereço.
- O processo terminou após uma alteração de código inválida.

### Diagnóstico

```bash
curl -i http://127.0.0.1:8000/health
```

Verificar o terminal do Uvicorn: deve indicar que a aplicação arrancou e está a escutar na porta esperada.

### Possíveis soluções

1. Corrigir primeiro o erro apresentado no terminal.
2. Reiniciar o servidor a partir de `backend/`:

```bash
python -m uvicorn app.main:app --reload
```

3. Confirmar que o URL corresponde ao endereço e à porta anunciados pelo Uvicorn.

### Lição aprendida

Uma ligação recusada é um **sintoma de indisponibilidade do serviço**, não necessariamente um problema no navegador. Investigar primeiro os logs do backend.

---

## 3. String sem interpolação: `"Hello, {name}!"`

### Descrição do erro

Código inicial:

```python
message = "Hello, {name}!"
```

Esta string contém literalmente `{name}`; não insere o valor do parâmetro.

### Possível causa

Esquecer o prefixo `f` de uma *formatted string literal* (*f-string*).

O f significa Formatted String Literal, conhecido como f-string (string formatada).

É um recurso do Python que permite inserir variáveis e expressões diretamente dentro de uma string, utilizando chaves {}.

### Solução

```python
message = f"Hello, {name}!"
```

Se `name` for `everton`, o resultado é `Hello, everton!`.

### Lição aprendida

O Python só interpola expressões entre chavetas quando se utiliza uma f-string (ou outra técnica explícita de formatação).

---

## 4. `return {message}` cria um `set`, não um `dict`

### Descrição do erro

Código inicial:

```python
return {message}
```

Em Python, uma expressão com um único elemento entre chavetas cria um **conjunto (*set*)**. O formato pedido para o endpoint era um objeto JSON com a chave `message`.

### Possível causa

Confundir a sintaxe de conjuntos com a de dicionários.

### Solução

```python
return {"message": message}
```

### Lição aprendida

```python
{"hello"}             # set
{"message": "hello"}  # dict
{}                    # dict vazio
set()                 # set vazio
```

O FastAPI pode serializar certos conjuntos, mas isso não os transforma no formato de resposta desejado.

---

## 5. Anotação de retorno incompatível: `-> str`

### Descrição do problema

O endpoint foi inicialmente declarado com retorno `str`, mas deveria devolver um dicionário:

```python
async def hello(name) -> str:
    ...
```

### Possíveis causas

- Confusão entre o tipo da mensagem (`str`) e o tipo da resposta completa (`dict`).
- Falta de anotação do parâmetro de caminho.

### Solução

```python
async def hello(name: str) -> dict[str, str]:
    ...
```

### Lição aprendida

As anotações de tipo (*type hints*) documentam o contrato esperado da função e ajudam ferramentas de análise estática. O Python não as impõe automaticamente em todas as chamadas.

---

## 6. Implementação final validada: `/hello/{name}`

```python
@app.get("/hello/{name}")
async def hello(name: str) -> dict[str, str]:
    hello_message = f"Hello, {name}!"
    return {"message": hello_message}
```

**Teste realizado:**

```text
GET http://127.0.0.1:8000/hello/everton
```

**Resposta observada:**

```json
{"message":"Hello, everton!"}
```

O teste confirma a leitura do parâmetro de caminho (*path parameter*), a interpolação da string e a serialização da resposta como JSON.

---

## 7. Checklist de diagnóstico rápido

Quando a API deixar de responder:

1. Confirmar o diretório atual com `pwd`.
2. Confirmar a presença de `app/main.py` com `ls -la app/`.
3. Confirmar o interpretador ativo com `which python`.
4. Tentar importar a aplicação: `python -c "from app.main import app; print(app.title)"`.
5. Executar `python -m uvicorn app.main:app --reload` a partir de `backend/`.
6. Ler a **primeira mensagem de erro relevante** no traceback, não apenas a última linha.
7. Testar `curl -i http://127.0.0.1:8000/health`.
8. Testar o endpoint no Swagger UI: `http://127.0.0.1:8000/docs`.

## 8. Resumo

| Problema | Conceito | Solução principal |
|---|---|---|
| `ModuleNotFoundError` | Importação de módulos | Executar a partir do diretório correto e verificar os caminhos |
| `ERR_CONNECTION_REFUSED` | Disponibilidade do servidor | Corrigir o arranque do Uvicorn e verificar a porta |
| `{name}` aparece literalmente | *f-string* | Utilizar `f"Hello, {name}!"` |
| `{message}` não é um dicionário | `set` vs. `dict` | Devolver `{"message": message}` |
| `-> str` não corresponde à resposta | *Type hints* | Utilizar `-> dict[str, str]` |

## 9. Próximo passo

Consolidar os conceitos de **parâmetros de caminho (*path parameters*)** e **parâmetros de consulta (*query parameters*)**, comparando:

```text
/hello/everton
/hello?name=everton
```

Depois, avançar para a integração com PostgreSQL e SQLAlchemy.
