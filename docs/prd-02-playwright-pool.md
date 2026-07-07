# PRD-02: Completar cobertura do playwright_pool.py

**Status:** Aprovado  
**Fase:** 2/7  
**Esforço estimado:** ~40 minutos  
**Ganho de cobertura:** 29% → 95% (+7.2pp — 30 statements)

---

## Objetivo

Cobrir as 30 linhas não testadas de `app/extensions/playwright_pool.py`, mockando o `async_playwright` para evitar dependência de Chromium real.

## Estratégia de teste

Usar `unittest.mock.patch` em `playwright.async_api.async_playwright` para simular o browser pool sem lançar Chromium. Cada teste deve restaurar os globais `_playwright`, `_browser`, `_playwright_ctx` para `None` em `setup_method`.

## Cenários a testar

### 1. ensure_browser — primeira chamada (linhas 26-30)

**Entrada:** `await ensure_browser()`

**Setup:** `_browser = None`

**Mock:** `async_playwright()` → context mock com `__aenter__` retornando playwright mock, `playwright.chromium.launch(headless=True)` retornando browser mock.

**Verificação:** `_browser` não é mais None; `async_playwright` foi chamado.

### 2. ensure_browser — idempotente (linha 27)

**Entrada:** `await ensure_browser()` (2ª chamada)

**Setup:** `_browser` já definido (browser mock)

**Verificação:** `async_playwright` NÃO é chamado de novo (retorno precoce).

### 3. ensure_browser_sync — com event loop rodando (linhas 45-50)

**Entrada:** `ensure_browser_sync()`

**Setup:** `_browser = None`, event loop em execução

**Verificação:** `loop.create_task` foi chamado com `ensure_browser()`.

### 4. ensure_browser_sync — sem loop rodando (linhas 51-52)

**Entrada:** `ensure_browser_sync()`

**Setup:** `_browser = None`, event loop existe mas NÃO está rodando

**Verificação:** `loop.run_until_complete(ensure_browser(...))` foi chamado.

### 5. ensure_browser_sync — sem event loop (linhas 53-54)

**Entrada:** `ensure_browser_sync()`

**Setup:** `asyncio.get_event_loop()` levanta `RuntimeError`

**Verificação:** `asyncio.run(ensure_browser(...))` foi chamado.

### 6. new_page (linhas 62-63)

**Entrada:** `await new_page()`

**Setup:** `_browser` já definido (browser mock)

**Verificação:** Retorna resultado de `_browser.new_page()`.

### 7. get_pdf_from_html — sucesso (linhas 77-92)

**Entrada:** `await get_pdf_from_html("<html>ok</html>")`

**Setup:** `_browser` já definido, `new_page` mockada

**Verificação:** `page.set_content("<html>ok</html>")` foi chamado; `page.pdf()` foi chamado com defaults; `page.close()` foi chamado no finally; retorna bytes.

### 8. get_pdf_from_html — erro (linhas 77-92, finally)

**Entrada:** `await get_pdf_from_html("<html>ok</html>")`

**Setup:** `page.set_content` levanta exceção

**Verificação:** `page.close()` é chamado no finally mesmo com erro.

### 9. get_pdf_from_html — kwargs personalizados (linhas 80-89)

**Entrada:** `await get_pdf_from_html("...", format="Letter", header_template="X", margin={"top": "0"})`

**Verificação:** `page.pdf()` recebe os kwargs passados.

### 10. close_browser — browser e ctx existem (linhas 98-105)

**Entrada:** `await close_browser()`

**Setup:** `_browser` e `_playwright_ctx` definidos

**Verificação:** `_browser.close()` chamado; `_playwright_ctx.__aexit__` chamado; globais voltam a None.

### 11. close_browser — sem browser (linhas 102-104)

**Entrada:** `await close_browser()`

**Setup:** `_browser = None`, `_playwright_ctx` definido

**Verificação:** Apenas `__aexit__` é chamado; globais voltam a None.

## Critérios de aceite

- [ ] Todos os 11 cenários passam
- [ ] Cobertura de `playwright_pool.py` atinge ≥ 95%
- [ ] `ruff check .` limpo
- [ ] Nenhum teste real de Playwright (sem Chromium)
- [ ] Globais são resetados entre testes (setup/teardown)

## Arquivos afetados

- `tests/test_playwright_pool.py` (novo — ~90 linhas)
