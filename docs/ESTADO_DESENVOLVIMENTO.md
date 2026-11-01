# Estado da implementação inicial

## Implementado no código

- RF01: cadastro de ferramentas.
- RF02: cadastro de moradores.
- RF03: empréstimo de ferramenta disponível, com prazo e responsável.
- RF04: devolução e atualização do estado.
- RF05: catálogo público com pesquisa e filtros.
- RF06: controle de atrasos calculado por data.
- RNF01/RNF02: base de autenticação com scrypt, sessão, CSRF, autorização, SQL parametrizado, escape Jinja2 e limitação de tentativas.
- RNF04: estilos responsivos, rótulos e estados textuais, navegação por teclado prevista no HTML.

## Verificação realizada neste ambiente

- Compilação sintática dos arquivos Python.
- Compilação dos templates Jinja2.
- Teste SQLite isolado de esquema e integridade do empréstimo único.
- Renderização visual estática das três telas a partir do HTML/CSS.

## Verificação pendente

- Instalação das dependências Flask/Werkzeug em ambiente com internet (indisponível aqui).
- Execução dos testes de aplicação com `pytest` usando o servidor Flask.
- Testes reais de navegação, acessibilidade e desempenho no sistema publicado.
- Dois ciclos de validação com representante externo real e ajustes após feedback.

Não apresente as prévias HTML ou as capturas como evidência de testes de back-end concluídos.
