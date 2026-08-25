#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "$0")/.."

echo "===== DJANGO ====="
docker compose exec -T web python manage.py check

echo "===== TESTES ====="
docker compose exec -T web python manage.py test prayers -v 1

echo "===== HEALTH ====="
curl -fsS http://127.0.0.1:9400/health/
echo

echo "===== STATIC ====="
curl -sS -o /tmp/pedido_oracao_app.css -w 'HTTP_CSS=%{http_code} SIZE=%{size_download}\n' http://127.0.0.1:9400/static/css/app.css

echo "===== CONTAINERS ====="
docker compose ps
