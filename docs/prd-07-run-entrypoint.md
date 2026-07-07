# PRD-07: Completar cobertura do entrypoint (run.py)

**Status:** Aprovado  
**Fase:** 7/7 (opcional)  
**Esforço estimado:** ~30 minutos  
**Ganho de cobertura:** 0% → 85% (+5.3pp — 22 statements)

---

## Objetivo

Cobrir as 22 linhas não testadas de `app/run.py`, especificamente a função `init_modules` que descobre e carrega módulos dinamicamente.

## Estratégia de teste

Testar `init_modules()` isoladamente, com mock de:
- `os.listdir` para controlar quais diretórios/módulos existem
- `importlib.util.spec_from_file_location` para evitar imports reais
- `robyn_app` mockado para verificar chamadas

## Cenários a testar

### 1. init_modules — módulo com init_module (linhas 25-32)

**Setup:** Mock `os.listdir` para retornar `["meu_modulo"]`. Mock `os.path.isdir` para True. Mock `os.path.isfile` para True. Criar spec mock que tem `init_module`.

**Entrada:** `init_modules(mock_app)`

**Verificação:**
- `spec.loader.exec_module` é chamado
- `module.init_module(mock_app)` é chamado
- `basic_logger.info` é chamado com `"Initialized module: meu_modulo"`

### 2. init_modules — módulo sem init_module (linha 29-30)

**Setup:** Similar ao anterior, mas o módulo mock não tem atributo `init_module`.

**Verificação:**
- `spec.loader.exec_module` é chamado
- `module.init_module` NÃO é chamado
- Nenhum logger.info para inicialização

### 3. init_modules — falha no carregamento (linhas 33-34)

**Setup:** `spec.loader.exec_module` levanta exceção.

**Verificação:**
- `basic_logger.exception` é chamado com `"Failed to initialize module meu_modulo"`

### 4. init_modules — ignora diretórios sem __init__.py (linhas 21-23)

**Setup:** `os.listdir` retorna `["mod_valido", "mod_invalido"]`. `os.path.isfile` para `mod_valido/__init__.py` retorna True, para `mod_invalido/__init__.py` retorna False.

**Verificação:** Apenas `mod_valido` é processado.

### 5. init_modules — ignora __pycache__ e __ (linha 21)

**Setup:** `os.listdir` retorna `["__pycache__", "meu_modulo"]`.

**Verificação:** `__pycache__` é ignorado (não é processado).

### 6. main() — __name__ == "__main__" (linhas 47-48)

**Setup:** Mock `app.start`.

**Entrada:** Simular `if __name__ == "__main__"` via chamada direta a `main()`.

**Verificação:** `app.start()` é chamado.

## Observação importante

O módulo `run.py` é executado no momento da importação (linha 37: `init_modules(app)`). Para testar `init_modules` isoladamente, precisamos **mockar** as funções **antes** de importar `run.py`, ou testar a função `init_modules` sem importar o módulo como um todo. Abordagem recomendada:

```python
# Extrair a função init_modules para teste
import run
# run já executou init_modules(app) na importação
# Para isolar, podemos mockar os módulos externos antes
```

Melhor abordagem: **importar `init_modules` sem executar o módulo** — mas como o módulo tem `init_modules(app)` na linha 37, isso não é possível sem mock prévio.

**Solução:** Usar `unittest.mock.patch` para mockar `os.listdir`, `importlib`, etc. antes de importar o módulo:

```python
with (
    patch("os.listdir", return_value=["meu_modulo"]),
    patch("os.path.isdir", return_value=True),
    patch("os.path.isfile", return_value=True),
    patch("importlib.util.spec_from_file_location") as mock_spec,
    patch("app.run.basic_logger"),
):
    from app.run import init_modules
    init_modules(mock_app)
```

## Recomendação

Esta fase é **opcional**. O arquivo `run.py` é o entrypoint da aplicação e naturalmente é coberto por testes de integração. A função `init_modules` depende fortemente de `os.listdir` e `importlib`, exigindo mocks frágeis. Considere priorizar apenas se houver exigência rigorosa de cobertura.

## Critérios de aceite (se implementada)

- [ ] Os 6 cenários passam
- [ ] Cobertura de `run.py` atinge ≥ 85%
- [ ] `ruff check .` limpo
- [ ] Nenhum módulo real é importado durante os testes
- [ ] Mocks são restaurados após cada teste

## Arquivos afetados

- `tests/test_run.py` (novo — ~80 linhas)
