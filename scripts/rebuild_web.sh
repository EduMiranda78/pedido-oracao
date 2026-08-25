#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "$0")/.."

echo "===== VALIDANDO COMPOSE ====="
docker compose config --quiet

echo "===== BUILD WEB ====="
docker compose build web

echo "===== RECRIANDO SOMENTE O WEB ====="
docker compose up -d --no-deps --force-recreate web

echo "===== AGUARDANDO HEALTHCHECK ====="
for i in $(seq 1 20); do
  if curl -fsS http://127.0.0.1:9400/health/ >/dev/null 2>&1; then
    echo "Aplicação respondeu com sucesso."
    break
  fi
  if [ "$i" -eq 20 ]; then
    echo "ERRO: aplicação não respondeu ao healthcheck." >&2
    docker compose logs --tail=80 web >&2
    exit 1
  fi
  sleep 2
done

echo "===== CSS ====="
HTTP_CSS=$(curl -sS -o /tmp/pedido_oracao_app.css -w '%{http_code}' http://127.0.0.1:9400/static/css/app.css)
SIZE_CSS=$(wc -c </tmp/pedido_oracao_app.css)
echo "HTTP_CSS=$HTTP_CSS SIZE=$SIZE_CSS"
if [ "$HTTP_CSS" != "200" ] || [ "$SIZE_CSS" -lt 10000 ]; then
  echo "ERRO: CSS não foi publicado corretamente." >&2
  exit 1
fi

echo "===== STATUS ====="
docker compose ps

echo "===== CONCLUÍDO ====="
