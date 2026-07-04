# Guia de Agentes de IA - ISIS Report

Este documento orienta agentes de codificação sobre como manter e evoluir o projeto respeitando os padrões estabelecidos.

## Regras de Ouro
1. **Async-First:** Nunca use chamadas bloqueantes. Prefira `async def` e use `await` para I/O e templates.
2. **Pandas para Lógica:** Toda agregação ou cálculo de agrupamento deve ser feito via Pandas no serviço, não no template.
3. **Nomenclatura:** Classes e arquivos em Inglês. Métodos internos de pipeline de serviço em Português (`__obter_dados`, `__tratar_dados`).

## Workflow de Desenvolvimento

### Setup do Ambiente
```bash
# Instalar dependências e Playwright
./dev/dependencies.sh
```

### Criando um Novo Módulo
1. Crie a pasta em `app/modules/{nome_do_modulo}`.
2. Implemente `__init__.py` com `init_module(app)`.
3. Crie `router.py` e a pasta `routes/` para definir os endpoints.
4. Implemente a lógica de negócio em `services/{nome_do_modulo}.py`.

### Qualidade de Código
Antes de enviar qualquer alteração:
- Execute o linter: `python -m ruff check . --fix`
- Execute os testes: `pytest -q`

## Convenções de Template
- Os templates estão em `app/templates/`.
- Use `relatorio_base.j2` como base para novos relatórios.
- Utilize a função `fmt(valor, mascara)` disponível no contexto do Jinja para formatação de moeda e datas conforme o locale.

## Tratamento de Erros
- Logs devem ser feitos via `extensions.log.basic_logger`.
- Erros na geração de PDF devem garantir o fechamento da página no Playwright via bloco `finally`.

## Mensagens de Commit
Siga o padrão Conventional Commits:
- `feat:` para novas funcionalidades.
- `fix:` para correção de bugs.
- `refactor:` para melhorias de código sem alteração de comportamento.
```
