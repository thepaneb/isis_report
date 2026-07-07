# PRD-03: Completar cobertura do routes_loader

**Status:** Aprovado  
**Fase:** 3/7  
**Esforço estimado:** ~20 minutos  
**Ganho de cobertura:** 29% → 95% (+2.4pp — 10 statements)

---

## Objetivo

Cobrir as 10 linhas não testadas de `app/extensions/routes_loader/__init__.py`.

## Estratégia de teste

Criar estrutura de diretórios temporária com rota simulada. Usar `tempfile.TemporaryDirectory` para criar pastas `routes/` com arquivos `.py` válidos e inválidos. Mockar `importlib.util.spec_from_file_location` para controlar o comportamento de carregamento sem executar imports reais.

## Cenários a testar

### 1. init_routes — sucesso (linhas 15-27)

**Setup:** Diretório temporário com `routes/meu_modulo.py` contendo código válido. Mock `importlib` para executar o módulo sem side effects.

**Entrada:** `init_routes(__file__)` onde `__file__` aponta para um arquivo no temp dir.

**Verificação:** `basic_logger.info` é chamado com `"Loaded route: meu_modulo.py"`. O módulo é executado via `spec.loader.exec_module`.

### 2. init_routes — falha no carregamento (linhas 28-29)

**Setup:** Diretório temporário com `routes/falho.py`. Mock `spec.loader.exec_module` para levantar exceção.

**Verificação:** `basic_logger.exception` é chamado com `"Failed to load route falho.py"`.

### 3. init_routes — ignora __init__.py (linhas 19-20)

**Setup:** Diretório temporário com `routes/__init__.py` e `routes/valido.py`.

**Verificação:** Apenas `valido.py` é carregado. `__init__.py` é ignorado.

## Considerações técnicas

- O código usa `os.listdir(routes_dir)` e filtra por `.py` e não `__`. O teste deve criar arquivos com nomes que testem cada condição do filtro.
- Para evitar efeitos colaterais de import real, usar `unittest.mock.patch` em `importlib.util.spec_from_file_location` para retornar um spec mockável.

## Critérios de aceite

- [ ] Os 3 cenários passam
- [ ] Cobertura de `routes_loader/__init__.py` atinge ≥ 95%
- [ ] `ruff check .` limpo
- [ ] Diretórios temporários são limpos após os testes

## Arquivos afetados

- `tests/test_routes_loader.py` (novo — ~60 linhas)
