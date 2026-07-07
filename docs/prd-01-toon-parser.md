# PRD-01: Completar cobertura do toon_parser.py

**Status:** Aprovado  
**Fase:** 1/7  
**Esforço estimado:** ~10 minutos  
**Ganho de cobertura:** 95% → 100% (+1.9pp — 6 statements)

---

## Objetivo

Cobrir as 6 linhas restantes não testadas de `app/utils/toon_parser.py` (linhas 106-107, 148-150, 153).

## Cenários a testar

### 1. Dict vazio no fim do arquivo (linhas 106-107)

**Contexto:** Em `_parse_dict`, quando uma chave termina com `:` mas não há valor inline nem tokens filhos em nível mais profundo, o código faz `result[key] = {}`.

**Entrada:**
```python
parser._parse_dict([(0, "key:")], 0, 0)
```

**Comportamento esperado:** Retorna `{"key": {}}` com i=1.

### 2. Extra dict após dash item (linhas 148-150)

**Contexto:** Em `_parse_array`, após processar `- chave: valor`, se o próximo token estiver exatamente em `tok_level + 1`, ele é parseado como dict adicional e mesclado ao item atual.

**Entrada:**
```python
parser._parse_array([(1, "- nome: foo"), (2, "idade: 30")], 0, 1)
```

**Comportamento esperado:** Retorna `[{"nome": "foo", "idade": 30}]` com i=2.

### 3. Linha sem `- ` no escopo do array (linha 153)

**Contexto:** Em `_parse_array`, linhas no nível do array que não começam com `- ` são ignoradas (apenas `i += 1`).

**Entrada:**
```python
parser._parse_array([(1, "extra")], 0, 1)
```

**Comportamento esperado:** Retorna `[]` com i=1.

## Critérios de aceite

- [ ] Os 3 novos testes passam
- [ ] `pytest --cov=app/utils/toon_parser.py --cov-report=term-missing` mostra 100%
- [ ] `ruff check .` continua limpo
- [ ] Nenhum comportamento existente é alterado

## Arquivos afetados

- `tests/test_toon_parser.py` (adição de 3 testes)
