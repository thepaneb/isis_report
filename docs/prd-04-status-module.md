# PRD-04: Completar cobertura do módulo status

**Status:** Aprovado  
**Fase:** 4/7  
**Esforço estimado:** ~15 minutos  
**Ganho de cobertura:** 62% → 95% (+2.4pp — 5 statements)

---

## Objetivo

Cobrir as 5 linhas não testadas de:
- `app/modules/status/services/status.py` (linhas 19-21)
- `app/modules/status/__init__.py` (linhas 14-15)

## Cenários a testar

### 1. status_service — exceção real (linhas 19-21)

**Contexto:** O bloco `except` em `processar()` atualmente é dead code (a linha 18 `return {...}` nunca falha). Para cobri-lo, precisamos forçar uma exceção.

**Abordagem:** Usar `unittest.mock.patch.object` para substituir temporariamente o método `processar` por uma versão que simula o comportamento do except:

```python
async def _processar_falho(self):
    try:
        raise RuntimeError("erro simulado")
    except Exception as e:
        basic_logger.error("Error processing status: %s", e)
        return {"status": "unhealthy", "error": str(e)}
```

Ou, alternativamente, usar `unittest.mock.patch` para fazer o `return` da linha 18 levantar exceção (mais próximo do código real).

**Entrada:** `await service.processar()` com exceção forçada

**Verificação:**
- `basic_logger.error` é chamado com a mensagem de erro
- Retorno é `{"status": "unhealthy", "error": "erro simulado"}`

### 2. status/__init__.py — init_module (linhas 14-15)

**Setup:** Mock de `Robyn` via `unittest.mock.create_autospec` ou objeto simples com método `include_router`.

**Entrada:**
```python
init_module(mock_robyn_app)
```

**Verificação:**
- `mock_robyn_app.include_router` foi chamado com o router correto (`router` de `app/modules/status/router.py`)

## Observações

- As linhas 19-21 do `status.py` exigem que o método `processar` lance exceção. Como o código atual tem `try/except` em volta de uma linha que nunca falha, considere-se remover o `try/except` se ele não for necessário, eliminando a cobertura necessária. Isso é uma decisão de design — documentar e perguntar ao time.
- `status/__init__.py` depende de uma instância real de `Robyn`. O mock pode ser um objeto simples (`unittest.mock.MagicMock`) já que só usamos `include_router`.

## Critérios de aceite

- [ ] Os 2 cenários passam (ou 1, se o try/except for removido)
- [ ] Cobertura de ambos os arquivos atinge 100%
- [ ] `ruff check .` limpo
- [ ] Se o `try/except` for removido, o comportamento público do método não muda

## Arquivos afetados

- `tests/test_status_service.py` (modificação — 1 teste adicionado)
- `tests/test_status_init.py` (novo — ~20 linhas)
- Opcional: `app/modules/status/services/status.py` (remoção do try/except)
