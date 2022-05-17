## Como utilizar

Primeiro é necessário instalar as dependências:

```console
pip3 install -r LOCAL_DO_SFTP_UTILS/requirements.txt
```

O arquivo `main.py` deve ser executado de dentro do repositório para ele encontrar o arquivo `.vscode/sftp.json`.

### A lista de arquivos pode ser passada através de um arquivo
Os caminhos dos arquivos listados devem ser relativos ao repositório.

**exemplo.txt**
```txt
arquivo1.php
dir/arquivo2.php
```

```console
python3 LOCAL_DO_SFTP_UTILS/main.py update_remote --from-file exemplo.txt
```

### A lista de arquivos pode ser passada como a saída de um comando
```console
COMANDO | python3 LOCAL_DO_SFTP_UTILS/main.py update_remote --from-stdin
```

Exemplos de comandos:
```console
git diff HEAD~4 --name-only
```

```console
gh pr view 2782 --json files --jq .files.[].path
```

```console
find . | grep .py
```
## Alias

Editar o arquivo `/etc/profile.d/aliases.sh` no git bash para adicionar o atalho `sftp_utils`:

```shell
alias sftp_utils='python3 LOCAL_DO_SFTP_UTILS/main.py'
```

Depois reiniciar o git bash ou executar `source /etc/profile.d/aliases.sh`.
