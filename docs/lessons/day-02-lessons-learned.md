# FinanceTracker — Dia 2: Lições aprendidas

**Projeto:** FinanceTracker  
**Ambiente:** Ubuntu 24.04.4 LTS (`noble`), Python 3.12, Docker Engine + Compose V2, PostgreSQL 17  
**Objetivo:** preparar a persistência de dados e compreender os comandos e erros encontrados.

> Convenção: **Executado** identifica comandos que apareceram no histórico da sessão; **Recomendado** identifica comandos de diagnóstico ou continuidade. Os valores de versões refletem a execução documentada e podem mudar.

## 1. Arquitetura e conceitos

- **Docker Engine:** executa e gere containers.
- **Docker Compose:** define e coordena serviços a partir de `compose.yaml`.
- **Imagem:** modelo usado para criar um container; neste projeto, `postgres:17`.
- **Container:** instância isolada do PostgreSQL em execução.
- **Volume nomeado:** armazena dados independentemente do ciclo de vida do container.
- **PostgreSQL:** sistema de gestão de bases de dados relacionais (RDBMS).
- **SQLAlchemy:** biblioteca Python para acesso a bases de dados e mapeamento objeto-relacional (ORM); não é a base de dados.
- **Psycopg:** driver de comunicação Python–PostgreSQL.
- **Alembic:** ferramenta para migrações versionadas do esquema da base de dados.
- **`requirements.txt`:** registo das dependências e versões do ambiente Python.

## 2. Comandos de diagnóstico do Ubuntu

### `lsb_release -a` — Executado

- `lsb_release`: apresenta informações da distribuição Linux.
- `-a`: mostra todos os campos disponíveis.
- Resultado observado: Ubuntu 24.04.4 LTS, codename `noble`.

### `dpkg -l | grep -E 'docker|containerd|podman'` — Executado

- `dpkg`: gestor de pacotes Debian/Ubuntu.
- `-l`: lista pacotes registados.
- `|`: encaminha a saída do primeiro comando para o segundo (*pipe*).
- `grep`: filtra linhas de texto.
- `-E`: ativa expressões regulares estendidas.
- `'docker|containerd|podman'`: procura qualquer um dos três termos; `|` dentro da expressão significa “ou”.
- Resultado observado: nenhuma correspondência; não havia pacotes correspondentes registados pelo `dpkg`.

### `deactivate` — Executado

- Função disponibilizada pelo ambiente virtual Python; desativa o `.venv` na shell atual.
- Não desinstala Python nem altera o Docker.

## 3. Docker: comandos utilizados

### `docker --version` — Executado

- `docker`: interface de linha de comandos (CLI).
- `--version`: mostra a versão da ferramenta; não verifica por si só se o serviço Docker está operacional.
- Inicialmente: comando não encontrado.

### `sudo docker run hello-world` — Executado

- `sudo`: executa com privilégios administrativos.
- `docker run`: cria e inicia um container a partir de uma imagem.
- `hello-world`: nome da imagem de teste.
- Resultado observado: `Hello from Docker!`; Docker Engine operacional.

### `sudo usermod -aG docker "$USER"` — Executado

- `sudo`: privilégios administrativos.
- `usermod`: modifica uma conta de utilizador.
- `-a`: acrescenta aos grupos suplementares sem substituir os anteriores (*append*).
- `-G docker`: define `docker` como grupo suplementar a acrescentar.
- `"$USER"`: expansão da variável de ambiente com o utilizador atual.
- **Atenção:** membros do grupo `docker` têm acesso equivalente a `root` através do daemon Docker.

### `docker run --rm hello-world` — Executado

- `run`: cria e executa um container.
- `--rm`: remove automaticamente o container quando terminar.
- `hello-world`: imagem de teste.
- Erro observado inicialmente: `permission denied ... /var/run/docker.sock`.
- Causa: o processo da shell ainda não tinha os novos grupos suplementares aplicados.
- Solução: terminar sessão e entrar novamente, ou usar `newgrp docker` numa nova shell; verificar com `id -nG`.

### `source ~/.bashrc` — Executado

- `source`: executa comandos do ficheiro na shell atual.
- `~`: diretório pessoal.
- `.bashrc`: configuração do Bash.
- **Lição:** recarregar `.bashrc` não atualiza os grupos Linux da sessão.

### `newgrp docker` — Recomendado

- `newgrp`: inicia uma shell com o grupo indicado como grupo ativo.
- `docker`: grupo pretendido.
- Alternativa mais persistente: sair e voltar a iniciar sessão.

### `id -nG` — Recomendado

- `id`: mostra identidade e grupos do utilizador.
- `-n`: nomes em vez de IDs numéricos.
- `-G`: todos os grupos suplementares e primário.
- Verificar se `docker` está presente.

## 4. Docker Compose: comandos utilizados

### `docker compose config` — Executado

- `docker`: CLI.
- `compose`: plugin de orquestração de serviços.
- `config`: valida, resolve e apresenta a configuração Compose.
- Primeiro erro: `services.db.enviroment ...`.
- **Causa:** propriedade `enviroment` escrita incorretamente; correto: `environment`.
- **Lição:** YAML pode ser sintaticamente válido e falhar na validação do esquema Compose.
- Após corrigir: a configuração foi apresentada com sucesso.

### `docker compose up -d db` — Executado

- `up`: cria/inicia serviços e recria containers quando necessário.
- `-d`: modo desligado do terminal (*detached*), em segundo plano.
- `db`: nome do serviço definido em `compose.yaml`.
- Observado: download da imagem `postgres:17`, criação de volume/rede e início do container.
- Depois de corrigir o nome do container, o Compose recriou-o; o volume nomeado preserva os dados, desde que continue montado e não seja removido.

### `docker compose ps` — Executado

- `ps`: lista os containers dos serviços do projeto e os seus estados.
- Observado: `financetracker-db`, imagem `postgres:17`, estado `Up`, porta `127.0.0.1:5432->5432/tcp`.
- `Up` não é garantia absoluta de que a aplicação dentro do container está pronta.

### `docker compose stop` — Executado

- `stop`: para os containers dos serviços sem os remover.
- Sem nome de serviço, atua sobre os serviços do projeto.
- `docker compose ps` ficou sem containers em execução.

### `docker compose exec db pg_isready -U financetracker -d financertracker` — Executado

- `exec`: executa um processo dentro de um container em execução.
- `db`: serviço Compose.
- `pg_isready`: verifica se o servidor PostgreSQL aceita ligações.
- `-U financetracker`: nome de utilizador usado na tentativa de verificação.
- `-d financertracker`: nome da base indicado, **com erro de digitação**.
- Resultado: `accepting connections`.
- **Lição:** `pg_isready` confirma disponibilidade do servidor, não valida necessariamente a existência da base ou a autenticação; usar `psql` para confirmar uma ligação real.

## 5. PostgreSQL e SQL

### `docker compose exec db psql -U financetracker -d financetracker` — Executado

- `psql`: cliente interativo PostgreSQL.
- `-U`: utilizador PostgreSQL.
- `-d`: nome da base de dados.
- Resultado: prompt `financetracker=#`.

### `SELECT current_user;` — Executado

- `SELECT`: consulta uma expressão ou dados.
- `current_user`: identidade da função de utilizador atual no PostgreSQL.
- `;`: encerra a instrução SQL.
- Resultado: `financetracker`.

### `SELECT current_database();` — Recomendado / tentativa com erro

- `current_database()`: função que devolve o nome da base atual.
- `()`: chamada de função sem argumentos.
- `;`: termina a instrução.
- Erro cometido: `SELECT current_database():` — dois-pontos no lugar de ponto e vírgula.
- Prompt `financetracker-#`: instrução ainda em construção.
- `\r`: limpa o buffer de consulta do `psql`; `Ctrl+C` também cancela a entrada atual.

### `CREATE TEMP TABLE test_transactions (id INTEGER, description VARCHAR(100), amount NUMERIC(12, 2));` — Executado

- `CREATE TABLE`: cria tabela.
- `TEMP`: torna a tabela temporária, associada à sessão atual.
- `test_transactions`: nome da tabela.
- `id INTEGER`: coluna de números inteiros.
- `description VARCHAR(100)`: texto variável até 100 caracteres.
- `amount NUMERIC(12, 2)`: decimal exato com até 12 dígitos totais, 2 após a vírgula.
- Resultado: `CREATE TABLE`.

### `INSERT INTO test_transactions VALUES (1, 'Supermercado', 45.90);` — Executado

- `INSERT INTO`: insere linha na tabela indicada.
- `VALUES`: fornece os valores na ordem das colunas, pois não foi especificada uma lista de colunas.
- `(1, 'Supermercado', 45.90)`: inteiro, texto SQL entre aspas simples e valor numérico.
- `;`: termina o comando, mesmo se for escrito na linha seguinte.
- Resultado: `INSERT 0 1` — uma linha inserida; o `0` é o campo OID legado da resposta.
- **Boa prática:** nomear as colunas no `INSERT` em código de produção.

### `SELECT * FROM test_transactions;` — Executado

- `SELECT`: consulta dados.
- `*`: todas as colunas.
- `FROM`: indica a tabela.
- `test_transactions`: tabela de origem.
- Resultado observado: `1 | Supermercado | 45.90`.
- **Lição:** a tabela temporária desaparece quando a sessão `psql` termina; isto é diferente da persistência do volume Docker.

## 6. Python: ambiente virtual e dependências

### `which python` — Executado

- `which`: mostra o executável encontrado no `PATH`.
- `python`: interpretador solicitado.
- Resultado: `backend/.venv/bin/python`.

### `python -m pip --version` — Executado

- `python`: interpretador ativo.
- `-m pip`: executa o módulo `pip` através desse interpretador.
- `--version`: apresenta versão e localização do `pip`.
- Resultado: `pip 24.0`, Python 3.12, dentro do `.venv`.

### `python -m pip install sqlalchemy "psycopg[binary]" alambic` — Executado com erro

- `install`: instala distribuições Python.
- `sqlalchemy`: biblioteca ORM.
- `"psycopg[binary]"`: instala Psycopg com a opção extra `binary`; aspas protegem os colchetes da interpretação da shell.
- `alambic`: **erro de digitação**; nome correto é `alembic`.
- Resultado: `No matching distribution found for alambic`.
- **Lição:** não assumir que os outros pacotes foram instalados após falha na resolução de dependências.

### `python -m pip install sqlalchemy "psycopg[binary]" alembic` — Recomendado e posteriormente confirmado no ambiente

- Instala SQLAlchemy, Psycopg e Alembic.
- A presença no `requirements.txt` confirma que os pacotes foram instalados no ambiente, embora a execução exata do comando corrigido não tenha sido mostrada.

### `python -m pip show sqlalchemy psycopg alembic` — Executado antes da instalação

- `show`: mostra metadados de distribuições instaladas.
- Os três nomes são os pacotes a verificar.
- Resultado inicial: `Package(s) not found`.

### `python -m pip freeze > requirements.txt` — Recomendado; ficheiro resultante apresentado

- `freeze`: lista as distribuições instaladas e as versões fixadas.
- `>`: redireciona a saída, substituindo o conteúdo do ficheiro.
- `requirements.txt`: ficheiro de dependências do backend.
- Foram observados: `fastapi==0.162.0`, `uvicorn==0.54.0`, `SQLAlchemy==2.1.8`, `psycopg==3.3.8`, `psycopg-binary==3.3.8`, `alembic==1.20.1`, entre outros.
- Dependências transitivas também aparecem no `pip freeze`.

### `cat requirements.txt` — Executado

- `cat`: escreve o conteúdo do ficheiro no terminal.
- `requirements.txt`: caminho do ficheiro lido.

### `python -c "import sqlalchemy, psycopg, alembic; print('All imports OK')"` — Recomendado

- `-c`: executa o código Python fornecido como argumento.
- `import`: verifica se os módulos podem ser importados.
- `print`: mostra mensagem de confirmação.
- **Ainda não há saída deste teste no histórico.**

## 7. Erros e soluções resumidos

| Sintoma | Causa | Correção / diagnóstico |
|---|---|---|
| `docker: command not found` | Docker não instalado ou fora do PATH | Instalar Docker Engine e Compose; verificar `docker --version` |
| `permission denied ... docker.sock` | Sessão sem grupo `docker` ativo | `id -nG`, nova sessão ou `newgrp docker`; avaliar implicações de segurança |
| `no configuration file provided` | `compose.yaml` ausente ou noutro diretório | `pwd`, `ls -la`, criar o ficheiro ou usar `docker compose -f caminho/compose.yaml ...` |
| `services.db.enviroment` | Chave Compose escrita incorretamente | Trocar `enviroment` por `environment`; `docker compose config` |
| `pg_isready` aceita nome incorreto | Verifica prontidão, não a existência da base | Testar ligação real com `psql -U ... -d ...` |
| Prompt `financetracker-#` | Instrução SQL não terminada | `;` para concluir ou `\r` para limpar |
| `No matching distribution found for alambic` | Nome de pacote incorreto | Instalar `alembic` |
| `pip show` não encontra pacotes | Pacotes não instalados no interpretador ativo | `which python`; `python -m pip install ...` |

## 8. Checklist de encerramento

- [x] Confirmar Ubuntu 24.04.4 LTS.
- [x] Instalar Docker e validar `hello-world` com `sudo`.
- [x] Criar e validar `compose.yaml`.
- [x] Iniciar PostgreSQL 17 e verificar `docker compose ps`.
- [x] Aceder ao `psql` e consultar `current_user`.
- [x] Criar tabela temporária, inserir e consultar um registo.
- [x] Registar SQLAlchemy, Psycopg e Alembic no `requirements.txt`.
- [ ] Confirmar importação conjunta dos três módulos com `python -c ...` (sem resultado apresentado).

**Próxima etapa:** implementar modelos SQLAlchemy e a ligação real do FastAPI à base PostgreSQL; ainda não foram implementados no Dia 2.
