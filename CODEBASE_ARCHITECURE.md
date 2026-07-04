# ISIS Report - Arquitetura do Sistema

## Visão Geral
O ISIS Report é um serviço de alta performance para geração de relatórios dinâmicos (HTML/PDF) utilizando Python 3.14+, Robyn, Pandas e Playwright.

## Core Stack
- **Web Framework:** [Robyn](https://robyn.io/) (Async, focado em performance).
- **Data Engine:** [Pandas](https://pandas.pydata.org/) (Tratamento de agrupamentos e agregações).
- **Template Engine:** [Jinja2](https://jinja.palletsprojects.com/) (Async rendering).
- **PDF Engine:** [Playwright](https://playwright.dev/python/) (Conversão headless via Chromium).
- **Package Manager:** [uv](https://github.com/astral-sh/uv).

## Padrões de Design Implementados

### 1. Pluggable Module System
O sistema utiliza um carregamento dinâmico de módulos localizado em `app/run.py`. 
- Cada diretório em `app/modules/` que contém um `__init__.py` com a função `init_module(robyn_app)` é automaticamente registrado.
- Isso permite a adição de novos tipos de relatórios ou funcionalidades sem alterar o núcleo da aplicação.

### 2. Service Pattern (Pipeline de Relatório)
Os serviços de relatório (ex: `TabularService`) seguem um pipeline estrito de processamento assíncrono:
1.  `__obter_dados()`: Recuperação de dados (atualmente via mock em `app/ds/`).
2.  `__tratar_dados()`: Transformação via Pandas (agrupamentos, somatórios).
3.  `__gerar_html()`: Renderização do template Jinja2.
4.  `__gerar_pdf()`: Conversão do HTML para PDF via Playwright (reutilizando o pool de browser).

### 3. Extension Pattern
Funcionalidades globais são isoladas em `app/extensions/`:
- `jinja_template`: Configura o ambiente assíncrono do Jinja2.
- `log`: Centraliza logs estruturados com rotação diária.
- `routes_loader`: Auxilia no registro automático de sub-rotas.
- `playwright_pool`: Gerencia a instância do browser para evitar overhead de inicialização por request.

## Estrutura de Diretórios

```text
app/
├── ds/                # Data Sources (Mock/Data access)
├── extensions/        # Framework wrappers (Jinja, Log, Playwright)
├── modules/           # Funcionalidades plugáveis
│   ├── tabular/       # Relatórios com agrupamentos complexos
│   └── status/        # Health checks
├── templates/         # Arquivos .j2 (Jinja2)
├── constants.py       # Configurações globais de layout
└── run.py             # Entry point e inicializador
```

## Fluxo de Dados
1. O cliente envia um JSON para `/app/tabular` ou `/app/sections`.
2. O Router repassa o payload para o Service correspondente.
3. O Service utiliza Pandas para processar a lógica de `groupings` e `aggregations` definida no JSON.
4. O Jinja2 renderiza o HTML usando fragmentos específicos.
5. O Playwright converte o resultado final em bytes de PDF.
