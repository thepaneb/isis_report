# Guia de Agentes de IA - ISIS Report

Este documento orienta agentes de codificação sobre como manter e evoluir o projeto respeitando os padrões estabelecidos.

## Regras de Ouro
1. **Async-First:** Nunca use chamadas bloqueantes. Prefira `async def` e use `await` para I/O e templates.
2. **Nomenclatura:** Classes e arquivos em Inglês. Métodos internos de pipeline de serviço em Português (`__obter_dados`, `__tratar_dados`).
3. **OpenAPI com Models:** Documente todas as rotas com modelos `JsonBody` (request) e `JSONResponse` (response) para geração automática do Swagger.

## Estrutura de Módulos

```
app/modules/{nome_do_modulo}/
├── __init__.py          # init_module(app) com init_routes + include_router
├── router.py            # SubRouter com prefix
├── models/
│   └── {modulo}.py      # Schemas JsonBody/JSONResponse para OpenAPI
├── routes/
│   └── {modulo}.py      # Endpoints com type hints nos handlers
└── services/
    └── {modulo}_service.py  # Lógica de negócio herdando BaseReportService
```

## Workflow de Desenvolvimento

### Setup do Ambiente
```bash
# Instalar dependências e Playwright
./dev/dependencies.sh
```

### Criando um Novo Módulo
1. Implemente em `app/modules/{nome_do_modulo}/` seguindo a estrutura acima.
2. Crie modelos `JsonBody`/`JSONResponse` em `models/` para documentação OpenAPI.
3. Nos route handlers, anote o parâmetro do body com o modelo `JsonBody` e o retorno com `JSONResponse`.
4. Use `responses` no decorator da rota para documentar erros (ex.: `{500: {"model": ErrorResponse, "description": "..."}}`).

### Qualidade de Código
Antes de enviar qualquer alteração:
- Execute o linter: `ruff check . --fix`

## Convenções de Template
- Os templates estão em `app/templates/` com extensão `.jinja`.
- Use `relatorio_base.jinja` como base para novos relatórios.
- Utilize a função `fmt(valor, mascara)` disponível no contexto do Jinja para formatação de moeda e datas conforme o locale.

## Documentação OpenAPI / Swagger
- O Robyn gera automaticamente o Swagger UI em `/docs` e o schema em `/openapi.json`.
- Para documentar o corpo da requisição: crie uma classe herdando de `JsonBody` com annotations e use como type hint no handler.
- Para documentar a resposta de sucesso: use `JSONResponse` como type hint de retorno ou `response_model` no decorator.
- Para documentar respostas de erro: use o parâmetro `responses` no decorator com `{"model": MeuErrorModel}`.
- Exemplo:
  ```python
  from robyn.types import JsonBody, JSONResponse

  class MeuPayload(JsonBody):
      campo: str
      opcional: int | None = None

  class MeuErro(JSONResponse):
      error: str

  @router.post("", responses={500: {"model": MeuErro, "description": "Erro interno"}})
  async def handler(request: Request, body: MeuPayload):
      ...
  ```

## Tratamento de Erros
- Logs devem ser feitos via `extensions.log.basic_logger`.
- Erros na geração de PDF devem garantir o fechamento da página no Playwright via bloco `finally`.

## Mensagens de Commit
Siga o padrão Conventional Commits:
- `feat:` para novas funcionalidades.
- `fix:` para correção de bugs.
- `refactor:` para melhorias de código sem alteração de comportamento.
