# Instalação como aplicativo

O Grupo Rede - Pedidos de Oração é uma PWA e pode ser instalado no celular ou computador por navegadores compatíveis.

## Endereço

Use sempre o endereço HTTPS fornecido pela administração do sistema.

A instalação PWA não deve ser feita pelo endereço HTTP interno de produção.

## Android com Google Chrome

1. abra o sistema no Google Chrome;
2. toque no menu de três pontos;
3. escolha `Instalar app` ou `Adicionar à tela inicial`;
4. confirme a instalação;
5. abra o sistema pelo novo ícone criado no aparelho.

## Samsung Internet

1. abra o sistema no Samsung Internet;
2. abra o menu do navegador;
3. procure `Adicionar página a`;
4. escolha `Tela inicial`;
5. confirme.

Quando a opção não estiver disponível, utilize o Google Chrome.

## iPhone e iPad

1. abra o sistema no Safari;
2. toque em `Compartilhar`;
3. escolha `Adicionar à Tela de Início`;
4. confirme em `Adicionar`.

## Computador

No Google Chrome ou Microsoft Edge, a opção de instalação pode aparecer na barra de endereço ou no menu do navegador.

O Firefox desktop pode ler o manifest da PWA, mas não oferece a mesma experiência de instalação de Chrome e Edge.

## Requisitos técnicos

A origem deve usar HTTPS para que recursos PWA sejam considerados seguros pelos navegadores.

O projeto fornece:

- `/manifest.webmanifest`;
- `/sw.js`;
- `/offline/`;
- ícones 192x192 e 512x512.
