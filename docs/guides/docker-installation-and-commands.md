# FinanceTracker — Instalação e comandos Docker

**Ambiente documentado:** Ubuntu 24.04.4 LTS (`noble`), Docker Engine e Docker Compose V2. 
**Referência oficial:** https://docs.docker.com/engine/install/ubuntu/
**Segurança:** os comandos que usam `sudo` alteram a configuração do sistema. O grupo `docker` concede acesso equivalente a `root`.

## 1. Diagnóstico inicial

```bash
lsb_release -a
dpkg -l | grep -E 'docker|containerd|podman'
docker --version
docker compose version
```

- `lsb_release -a`: `-a` apresenta todos os dados da distribuição.
- `dpkg -l`: `-l` lista pacotes; `|` envia a saída a `grep`; `grep -E` usa regex estendida; `'docker|containerd|podman'` procura qualquer termo.
- `docker --version`: versão da CLI; não testa o daemon.
- `docker compose version`: versão do plugin Compose V2.

## 2. Instalação pelo repositório oficial

> Procedimento para Ubuntu 24.04. Antes de repetir numa máquina com instalações existentes, consultar a documentação oficial e resolver possíveis conflitos de pacotes.

### 2.1 Atualizar índices e instalar pré-requisitos

```bash
sudo apt update
sudo apt install ca-certificates curl
```

- `sudo`: privilégios administrativos.
- `apt update`: atualiza índices dos repositórios.
- `apt install`: instala pacotes.
- `ca-certificates`: certificados de confiança para ligações HTTPS.
- `curl`: ferramenta para descarregar dados via URL.

### 2.2 Configurar chave de assinatura

```bash
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

- `install -d`: cria diretório; `-m 0755`: permissões do diretório.
- `curl -f`: falha em erros HTTP; `-s`: silencioso; `-S`: mostra erros mesmo em modo silencioso; `-L`: segue redirecionamentos; `-o`: ficheiro de saída.
- `chmod a+r`: adiciona permissão de leitura para todos os utilizadores.
- `\` no fim da linha: continuação de comando na shell.

### 2.3 Configurar repositório APT

```bash
sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null <<REPO
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
REPO
sudo apt update
```

- `tee`: escreve o ficheiro com privilégios de `sudo`; `> /dev/null` descarta a cópia da saída.
- `<<REPO ... REPO`: *here-document*, que envia várias linhas ao comando.
- `$(...)`: substituição de comando; `. /etc/os-release` carrega variáveis do Ubuntu.
- `${UBUNTU_CODENAME:-$VERSION_CODENAME}`: usa o codename do Ubuntu ou o valor alternativo.
- `dpkg --print-architecture`: obtém a arquitetura do sistema.

### Instalar Docker Engine e Compose V2

```bash
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

- `docker-ce`: motor Docker.
- `docker-ce-cli`: interface de linha de comandos.
- `containerd.io`: gestão de containers.
- `docker-buildx-plugin`: construção de imagens.
- `docker-compose-plugin`: comando `docker compose`.

### Verificar a instalação

```bash
docker --version
docker compose version
sudo systemctl status docker
sudo docker run hello-world
```

- `--version`: versão da CLI.
- `systemctl status docker`: estado do serviço (sair com `q`).
- `docker run hello-world`: cria e executa container de teste.
- No projeto, o teste exibiu `Hello from Docker!`.

## 3. Permissões: executar sem sudo (opcional)

```bash
sudo usermod -aG docker "$USER"
```

- `usermod`: altera a conta.
- `-a`: acrescenta sem substituir grupos anteriores.
- `-G docker`: adiciona o grupo suplementar `docker`.
- `$USER`: variável com o utilizador atual.

**É necessário iniciar uma nova sessão**; `source ~/.bashrc` não atualiza grupos do processo. Alternativa temporária:

```bash
newgrp docker
id -nG
docker run --rm hello-world
```

- `newgrp docker`: abre shell com grupo ativo.
- `id -nG`: mostra os nomes dos grupos.
- `--rm`: remove container após terminar.

**Segurança:** membros do grupo `docker` podem obter privilégios equivalentes a `root`. Se preferires, utiliza Docker com `sudo` em vez de aderir ao grupo.

## 4. Ficheiro Compose do FinanceTracker

Guardar na raiz do repositório como `compose.yaml`:

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

- `db`: nome do serviço.
- `postgres:17`: imagem e etiqueta de versão.
- `container_name`: nome do container.
- `restart: unless-stopped`: política de reinício.
- `environment`: variáveis de ambiente (**não** `enviroment`).
- `ports`: `IP_host:porta_host:porta_container`; o IP local evita publicação em todas as interfaces.
- `postgres_data`: volume nomeado, que persiste dados entre recriações do container.
- `POSTGRES_*`: inicialização de utilizador, palavra-passe e base apenas quando o diretório de dados está vazio.

**Nota:** `dev_password` é uma senha de exemplo local; nunca utilizar credenciais reais no Git. Futuramente, mover para um `.env` não versionado.

## 5. Referência de comandos Compose

| Comando | Explicação |
|---|---|
| `docker compose config` | Valida e apresenta configuração resolvida. |
| `docker compose up -d db` | `up`: cria/inicia; `-d`: segundo plano; `db`: serviço. |
| `docker compose ps` | `ps`: lista estados dos containers do projeto. |
| `docker compose logs db` | `logs`: mostra mensagens do serviço. |
| `docker compose logs -f db` | `-f`: acompanha novas mensagens; `Ctrl+C` para parar. |
| `docker compose stop db` | `stop`: para sem remover. |
| `docker compose start db` | `start`: inicia container existente parado. |
| `docker compose down` | Remove containers e rede; mantém volumes nomeados por padrão. |
| `docker compose exec db sh` | `exec`: executa `sh` dentro do serviço. |
| `docker compose exec db pg_isready -U financetracker -d financetracker` | `-U`: utilizador; `-d`: base; verifica prontidão do servidor. |
| `docker compose exec db psql -U financetracker -d financetracker` | Abre uma ligação SQL real. |

**Atenção ao comando `docker compose down -v`:** `-v` remove volumes nomeados declarados pelo Compose e volumes anónimos ligados aos containers. Pode eliminar os dados do PostgreSQL; não o utilizar para paragem normal.

## 6. Outros comandos Docker úteis

```bash
docker ps
docker ps -a
docker images
docker volume ls
docker network ls
```

- `ps`: containers em execução; `-a`: inclui parados.
- `images`: imagens disponíveis localmente.
- `volume ls`: lista volumes.
- `network ls`: lista redes.

## 7. Erros encontrados e soluções

| Erro | Causa | Diagnóstico / solução |
|---|---|---|
| `docker: command not found` | Docker não instalado | Instalar e verificar `docker --version`. |
| `permission denied ... docker.sock` | Grupo `docker` não ativo na sessão | `id -nG`; iniciar nova sessão ou `newgrp docker`. |
| `no configuration file provided` | `compose.yaml` ausente ou diretório errado | `pwd`, `ls -la`; criar ficheiro ou usar `docker compose -f /caminho/compose.yaml config` (`-f` seleciona ficheiro). |
| `services.db.enviroment` | Chave inválida | Corrigir para `environment`; executar `docker compose config`. |
| Nome `financertracker-db` | Erro de digitação no `container_name` | Corrigir e executar `docker compose up -d db`. |
| Container `Up`, mas sem ligação | Serviço ainda não pronto ou credenciais incorretas | `docker compose logs db`, `pg_isready`, testar `psql`. |

## 8. Rotina de desenvolvimento

```bash
cd ~/Documentos/github_repos/FinanceTracker
docker compose up -d db
docker compose ps
docker compose exec db pg_isready -U financetracker -d financetracker
```

Para parar no fim do trabalho:

```bash
docker compose stop db
```

**Referências:** https://docs.docker.com/engine/install/ubuntu/ · https://docs.docker.com/compose/
