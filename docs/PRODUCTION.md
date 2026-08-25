# Execução em produção

## Componentes

A instalação de produção utiliza:

- Nginx como proxy HTTPS;
- Docker Compose;
- Gunicorn;
- Django;
- PostgreSQL 17;
- WhiteNoise.

## Portas

O Compose atual publica a aplicação web em:

```text
host :9400 -> container :8000
```

O PostgreSQL não publica porta no host.

No ambiente atual, uma camada Nginx HTTPS pode publicar a aplicação por uma porta externa segura e encaminhar para `127.0.0.1:9400`.

A porta HTTPS externa é uma decisão do servidor e não deve ser assumida como requisito do código.

## Inicialização do serviço web

O Compose executa:

```bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 60
```

## Healthcheck

Endpoint:

```text
/health/
```

Validação local:

```bash
curl -fsS http://127.0.0.1:9400/health/
```

## Deploy a partir do GitHub

Atualize o código sem criar merge automático:

```bash
git fetch origin
git merge --ff-only origin/main
```

Valide o Compose:

```bash
docker compose config --quiet
```

Construa somente o web:

```bash
docker compose build web
```

Recrie somente o serviço web:

```bash
docker compose up -d --no-deps --force-recreate web
```

Aguarde o healthcheck e valide:

```bash
docker compose ps
curl -fsS http://127.0.0.1:9400/health/
curl -sS -o /dev/null -w 'CSS=%{http_code}\n' \
  http://127.0.0.1:9400/static/css/app.css
docker compose logs --tail=50 web
```

## Banco de dados

Antes de migrations destrutivas ou alterações estruturais, faça `pg_dump`.

Exemplo:

```bash
docker compose exec -T db \
  sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' \
  > /caminho/seguro/pedido_oracao_backup.sql
```

Não armazene dumps dentro do repositório Git.

## HTTPS e proxy

Quando Nginx termina TLS e envia requisições ao Django por HTTP interno, preserve os cabeçalhos de proxy necessários, especialmente:

```nginx
proxy_set_header Host $http_host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto https;
```

O Django deve reconhecer corretamente o protocolo encaminhado pelo proxy.

## Variáveis de segurança HTTPS

O código não contém endereço, domínio ou porta pública de produção. Configure no `.env` local:

```env
DJANGO_SECURE_COOKIES=True
DJANGO_CSRF_TRUSTED_ORIGINS=https://seu-endereco-https.example
```

`DJANGO_CSRF_TRUSTED_ORIGINS` aceita múltiplas origens separadas por vírgula.

Com `DJANGO_SECURE_COOKIES=True`, cookies de sessão e CSRF são enviados somente por HTTPS. O endpoint HTTP interno pode continuar sendo usado para healthcheck e comunicação do proxy, mas o uso autenticado pelo navegador deve ocorrer pela origem HTTPS.

## Arquivos estáticos

O projeto usa:

```text
STATICFILES_DIRS -> static/
STATIC_ROOT      -> staticfiles/
```

`collectstatic` é executado antes do Gunicorn no startup do container web.

## Rollback

Em caso de falha:

1. preserve o banco;
2. volte o código para o commit anterior;
3. reconstrua somente a imagem `web`;
4. recrie somente o container `web`;
5. valide healthcheck e logs.

Evite remover o volume PostgreSQL durante rollback de código.
