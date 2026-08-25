# Changelog

## 1.1.7, 2026-08-24

- atualiza a documentação para refletir a visibilidade pública do repositório;
- remove endpoint de produção hardcoded de `config/settings.py`;
- parametriza `CSRF_TRUSTED_ORIGINS` via `DJANGO_CSRF_TRUSTED_ORIGINS`;
- parametriza cookies `Secure` via `DJANGO_SECURE_COOKIES`;
- ativa cookies seguros no ambiente de produção atual;
- mantém o HTTP interno disponível para healthcheck e proxy, com uso autenticado orientado a HTTPS;
- generaliza `.env.example` para evitar informações específicas do servidor;
- adiciona teste para a configuração HTTPS por variáveis de ambiente.

## 1.1.6, 2026-08-24

- remove o botão customizado de instalação da tela de login;
- remove mensagens de orientação de instalação da interface;
- mantém manifest, Service Worker, ícones e suporte PWA;
- instalação passa a ser feita diretamente pelo menu do navegador compatível.

## 1.1.5, 2026-08-24

- melhora a identificação de navegadores no fluxo PWA;
- diferencia orientações para Chrome, Edge, Samsung Internet, Firefox e iOS;
- preserva a instalação nativa quando o navegador oferece `beforeinstallprompt`.

## 1.1.4, 2026-08-24

- disponibiliza manifest na raiz com MIME próprio;
- ajusta `start_url` da PWA para o login;
- amplia o Service Worker para navegação e página offline;
- adiciona testes de formato instalável do manifest;
- adiciona testes de Service Worker e página offline.

## 1.1.3, 2026-08-24

- move o botão de instalação para o topo da tela de login;
- reforça o destaque visual da ação de instalação;
- melhora o tratamento do evento nativo de instalação do navegador.

## 1.1.2, 2026-08-24

- adiciona suporte inicial a PWA;
- adiciona manifest, Service Worker e ícones;
- adiciona links de LinkedIn e WhatsApp na tela de login;
- compacta o login para celulares e tablets;
- melhora adaptação à altura real da viewport móvel.

## 1.1.1, 2026-08-24

- adiciona o campo obrigatório `requester_origin`;
- integra a origem do solicitante ao cadastro, edição e pesquisa;
- inclui origem em listagem, detalhes, impressão e exportações;
- adiciona migration `0002_prayerrequest_requester_origin`.

## 1.1.0, 2026-08-24

- refaz a interface visual da aplicação;
- adiciona shell desktop com menu lateral;
- adiciona navegação inferior no celular;
- reorganiza dashboard, formulários, listagem e detalhes;
- melhora busca, filtros e paginação;
- melhora impressão e feedback de ações;
- corrige coleta e publicação de arquivos estáticos.

## 1.0.0, 2026-08-24

- primeira versão funcional;
- autenticação Django;
- cadastro e acompanhamento de pedidos;
- pedidos reservados;
- auditoria de alterações;
- pesquisa e filtros;
- exportação CSV, XLSX e PDF;
- impressão;
- PostgreSQL;
- Docker Compose;
- Gunicorn;
- healthcheck HTTP.
