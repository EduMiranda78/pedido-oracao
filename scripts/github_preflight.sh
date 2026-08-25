#!/usr/bin/env bash

set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail=0

ok() {
  printf 'OK: %s\n' "$1"
}

bad() {
  printf 'ERRO: %s\n' "$1" >&2
  fail=1
}

echo "===== GITHUB PREFLIGHT ====="

echo
echo "[1/8] Arquivos obrigatórios"
for path in README.md SECURITY.md CONTRIBUTING.md CHANGELOG.md .gitignore .dockerignore .env.example VERSION; do
  if [ -f "$path" ]; then
    ok "$path"
  else
    bad "arquivo ausente: $path"
  fi
done

echo
echo "[2/8] Segredos e arquivos de runtime"
if [ -f .env ]; then
  if git check-ignore -q .env 2>/dev/null; then
    ok ".env existe localmente e está ignorado pelo Git"
  else
    bad ".env existe e NÃO está ignorado pelo Git"
  fi
else
  ok ".env não está presente neste diretório"
fi

for pattern in '*.sql' '*.dump' '*.tar.gz' '*.zip'; do
  if find . -path './.git' -prune -o -type f -name "$pattern" -print | grep -q .; then
    echo "AVISO: existem arquivos $pattern no diretório; confirme que estão ignorados."
  fi
done

if [ -d backups ]; then
  if git check-ignore -q backups 2>/dev/null; then
    ok "backups/ está ignorado"
  else
    bad "backups/ não está ignorado"
  fi
fi

echo
echo "[3/8] Git ignore"
if git check-ignore -q .env 2>/dev/null; then
  ok ".env ignorado"
else
  bad ".env não foi reconhecido pelo .gitignore"
fi

for sample in backups/test.sql arquivo.sql arquivo.tar.gz staticfiles/test.css; do
  if git check-ignore -q "$sample" 2>/dev/null; then
    ok "$sample ignorado"
  else
    bad "$sample não está coberto pelo .gitignore"
  fi
done

echo
echo "[4/8] Busca por credenciais acidentais"
SECRET_HITS="$({ grep -RInE \
  --exclude-dir=.git \
  --exclude-dir=backups \
  --exclude='.env' \
  --exclude='*.png' \
  --exclude='*.jpg' \
  --exclude='*.jpeg' \
  '(BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16})' . || true; } )"

if [ -n "$SECRET_HITS" ]; then
  printf '%s\n' "$SECRET_HITS"
  bad "possível segredo encontrado"
else
  ok "nenhum padrão óbvio de chave/token encontrado"
fi

echo
echo "[5/8] Sintaxe Python"
if python3 -m compileall -q config prayers; then
  ok "compileall"
else
  bad "erro de sintaxe Python"
fi

echo
echo "[6/8] Docker Compose"
if [ -f .env ]; then
  if docker compose config -q; then
    ok "docker compose config"
  else
    bad "docker compose config falhou"
  fi
else
  echo "AVISO: .env ausente; validação do Compose não executada."
fi

echo
echo "[7/8] Arquivos que seriam versionados"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git status --short
  TRACKED_SENSITIVE="$(
    git ls-files \
      | grep -E '(^|/)\.env($|\.)|(^|/)backups?/|\.(sql|dump|tar\.gz|zip)$' \
      | grep -vE '(^|/)\.env\.example$' \
      || true
  )"
  if [ -n "$TRACKED_SENSITIVE" ]; then
    printf '%s\n' "$TRACKED_SENSITIVE"
    bad "arquivo sensível ou backup já está versionado"
  else
    ok "nenhum arquivo sensível listado por git ls-files"
  fi
else
  echo "Git ainda não inicializado. Esta verificação será repetida após git init."
fi

echo
echo "[8/8] Resultado"
if [ "$fail" -ne 0 ]; then
  echo "PREFLIGHT FALHOU"
  exit 1
fi

echo "PREFLIGHT OK"
