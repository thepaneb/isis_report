# PRD-06: Completar cobertura do módulo de log

**Status:** Aprovado  
**Fase:** 6/7 (opcional)  
**Esforço estimado:** ~10 minutos  
**Ganho de cobertura:** 95% → 100% (+0.2pp — 1 statement)

---

## Objetivo

Cobrir a linha 19 de `app/extensions/log/__init__.py`:
```python
os.makedirs(log_dir)
```

Esta linha só é executada quando o diretório `logs/` não existe.

## Desafio

`basic_logger` é uma variável **module-level** que é executada no momento da importação:

```python
basic_logger = get_basic_logger()
```

Quando os testes rodam, `app/extensions/log/__init__.py` já foi importado (via conftest.py e demais imports), e o diretório `logs/` já existe (criado pela própria importação). Portanto, para testar a linha 19, precisamos:

1. Remover o diretório `logs/`
2. Recarregar o módulo com `importlib.reload`
3. Testar
4. Restaurar o estado

## Abordagem

```python
import importlib
import os
import shutil
import tempfile

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")


def test_makedirs_na_criacao_do_logger():
    # Remover diretório de logs
    if os.path.exists(LOG_DIR):
        shutil.rmtree(LOG_DIR)

    # Recarregar módulo para executar get_basic_logger() de novo
    import extensions.log
    importlib.reload(extensions.log)

    # Verificar que o diretório foi criado
    assert os.path.exists(LOG_DIR)

    # Restaurar (recarregar de novo para evitar efeitos colaterais)
    importlib.reload(extensions.log)
```

## Riscos

- `importlib.reload` pode causar efeitos colaterais em outros módulos que já importaram `basic_logger`.
- O diretório `logs/` pode conter arquivos de log úteis para debugging — removê-lo pode atrapalhar.

## Recomendação

Esta fase é **opcional e de baixo valor**. A linha 19 é uma operação trivial (`os.makedirs`) cujo comportamento é bem conhecido e estável. A cobertura de 95% já é aceitável para este arquivo.

**Pular esta fase** a menos que haja exigência explícita de 100% de cobertura para todos os arquivos.

## Critérios de aceite (se implementada)

- [ ] Teste passa isoladamente
- [ ] `importlib.reload` não quebra outros testes na sessão
- [ ] `ruff check .` limpo
- [ ] Diretório `logs/` é restaurado ao final

## Arquivos afetados

- `tests/test_log.py` (novo — ~25 linhas)
