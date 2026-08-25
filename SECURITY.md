# Segurança

## Escopo

O Grupo Rede - Pedidos de Oração armazena pedidos que podem conter nomes, localidades, situações pessoais e outras informações potencialmente sensíveis.

Por esse motivo, privacidade, autenticação e controle de acesso fazem parte do núcleo do projeto e não devem ser tratados apenas como detalhes de interface.

## Recomendações

- mantenha o repositório privado;
- nunca versione `.env`, chaves, senhas ou tokens;
- nunca versione dumps PostgreSQL ou backups da aplicação;
- mantenha o banco sem porta publicada no host;
- exponha a aplicação externamente somente por HTTPS;
- mantenha `DEBUG=False` em produção;
- revise `ALLOWED_HOSTS` e origens CSRF ao alterar domínio, IP ou proxy;
- preserve cookies exclusivos desta aplicação em ambientes com vários apps no mesmo host;
- mantenha Docker, Python, Django, PostgreSQL e dependências atualizados;
- revise permissões antes de alterar regras de pedidos reservados;
- evite registrar conteúdo integral de pedidos em logs de aplicação ou proxy.

## Pedidos reservados

A regra de visibilidade de pedidos reservados é uma barreira de privacidade importante.

Antes de alterar `visible_queryset`, views de edição ou permissões administrativas, confirme por testes que:

- usuário comum não vê pedido reservado de outro usuário;
- criador continua vendo seu próprio pedido reservado;
- equipe administrativa autorizada continua tendo acesso;
- edição por usuário comum permanece limitada aos próprios registros.

## Credenciais

Credenciais devem existir somente em variáveis de ambiente e no `.env` local não versionado.

Se uma credencial for publicada acidentalmente, revogue ou substitua a credencial imediatamente. Apenas remover o arquivo do último commit não é suficiente quando o valor já entrou no histórico Git.

## Banco de dados e backups

Não envie ao GitHub:

- `*.sql`;
- `*.dump`;
- diretórios `backups/`;
- volumes PostgreSQL;
- arquivos compactados contendo o projeto em produção;
- logs com dados pessoais.

Backups devem ser armazenados fora do repositório e protegidos de acordo com a sensibilidade dos dados.

## HTTPS e PWA

O Service Worker e a instalação PWA devem ser usados em origem segura HTTPS.

Em produção, o Nginx deve encaminhar corretamente `X-Forwarded-Proto` para que o Django reconheça requisições HTTPS através do proxy reverso.

## Relato de problemas

Como o repositório é privado, registre problemas de segurança diretamente nas issues privadas do repositório ou comunique o mantenedor por canal privado.
