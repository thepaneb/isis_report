Resumo rápido do repositório

- Projeto: ISIS Report — serviço Python (Robyn) que gera relatórios HTML/PDF.
- Local: `app/` contém módulos, rotas, serviços e templates Jinja2.
- Testes: `pytest` (pytest-asyncio) — execução: `pytest -q`.
- Lint: `ruff` — correções automáticas: `ruff check . --fix`.

Como trabalhar aqui (para agentes):

- Sempre crie uma branch por tarefa: `feature/<curto-descritivo>`.
- Execute lint e testes localmente antes de commitar:

```bash
python -m pip install -r dev-requirements.txt
python -m ruff check . --fix
pytest -q
```

- Playwright: executar antes de testes que geram PDF / headless:

```bash
python -m playwright install chromium --with-deps --only-shell
```

- Commits: mensagens curtas e descritivas (prefixo `fix:`, `feat:`, `ci:`, `chore:`).
- Evite tocar em arquivos que não estejam relacionados à tarefa.

Padrões de código e convenções:

- Async-first: handlers e serviços devem usar `async def` e `await`.
- Templates Jinja2 estão em `app/templates/` (agente deve usar `Environment(enable_async=True)`).
- Playwright: prefira reutilizar browser / pool (não iniciar por requisição).

Quando abrir PR/merge:

- Garanta que `ruff check .` e `pytest -q` passem no CI.
- Atualize `CHANGELOG.md` quando fizer release manualmente.

Permissões e segredos:

- Nunca exponha tokens ou segredos nos commits.
- Para operações via API (PRs, runs), peça ao usuário um token com permissões necessárias.
