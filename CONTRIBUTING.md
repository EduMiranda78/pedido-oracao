# Contribuição e manutenção

Este é um projeto privado mantido por Eduardo Miranda.

## Fluxo sugerido

1. atualize `main`;
2. crie uma branch para a alteração;
3. faça mudanças pequenas e identificáveis;
4. rode os testes Django;
5. verifique migrations pendentes;
6. execute o preflight de GitHub;
7. revise alterações em segurança, Docker e `.env.example`;
8. abra um pull request para `main`.

## Validação local

```bash
docker compose run -T --rm web python manage.py check
docker compose run -T --rm web python manage.py makemigrations --check --dry-run
docker compose run -T --rm web python manage.py test prayers -v 2
bash scripts/github_preflight.sh
```

## Commits

Prefira mensagens objetivas, por exemplo:

```text
Adiciona campo de origem do solicitante
Melhora login responsivo
Corrige configuração de cookies CSRF
Aprimora suporte PWA
Documenta deploy via Nginx HTTPS
```

## Cuidados

Não inclua em commits:

- `.env`;
- chaves, senhas ou tokens;
- dumps PostgreSQL;
- backups;
- logs de produção;
- arquivos com pedidos reais exportados;
- capturas de tela com dados pessoais;
- arquivos compactados de produção.

## Alterações de banco

Quando houver mudança em models:

1. crie a migration;
2. revise a migration gerada;
3. execute os testes em banco temporário;
4. documente a mudança no `CHANGELOG.md`;
5. faça backup do banco antes do deploy em produção.
