# PRD-05: Completar cobertura do sistema de templates Jinja2

**Status:** Aprovado  
**Fase:** 5/7  
**Esforço estimado:** ~15 minutos  
**Ganho de cobertura:** 88% → 100% (+0.7pp — 2 statements)

---

## Objetivo

Cobrir as 2 linhas restantes não testadas:
- `app/extensions/jinja_template/__init__.py` linha 19 (`jinja_template.render_template`)
- `app/extensions/jinja_template/templating.py` linhas 33 e 39 (inicialização do `Environment` e `render`)

## Estratégia de teste

Criar template `.jinja` real em diretório temporário e usar `JinjaTemplate` diretamente, sem mocks, para exercitar o pipeline real de renderização.

## Cenários a testar

### 1. JinjaTemplate.render_template — template real (linhas 33, 39)

**Setup:** Criar diretório temporário com arquivo `teste.jinja`:
```jinja
Olá {{ nome }}!
```

**Entrada:**
```python
jt = JinjaTemplate(str(temp_dir))
result = await jt.render_template("teste.jinja", nome="Mundo")
```

**Verificação:**
- `result == "Olá Mundo!"`
- O `Environment` foi criado com `FileSystemLoader` apontando para o diretório correto

### 2. render_template — função de conveniência (linha 19 do __init__.py)

**Setup:** Mesmo diretório temporário com template. Importar `render_template` do módulo ou criar instância similar.

**Entrada:**
```python
from extensions.jinja_template import jinja_template
jinja_template.directory = str(temp_dir)  # redirecionar
```

**Verificação:** Retorna o HTML renderizado corretamente.

## Abordagem alternativa

Se for difícil usar diretamente o `render_template` de `extensions.jinja_template` (por ser module-level com path fixo), podemos:

1. Testar apenas `JinjaTemplate(directory, ...)` diretamente (já cobre linha 39)
2. Para cobrir linha 19, chamar `render_template` com mock de `jinja_template.render_template` e verificar que o delegado é chamado — mas isso já está coberto. A linha 19 só não está coberta porque os testes atuais mockam `render_template` no módulo consumidor.

**Solução:** Testar `render_template` sem mock, usando monkey-patch no `jinja_template.directory`:

```python
from extensions.jinja_template import jinja_template
original_dir = jinja_template.env.loader.searchpath
jinja_template.env.loader.searchpath = [str(temp_dir)]
# testar
jinja_template.env.loader.searchpath = original_dir
```

## Critérios de aceite

- [ ] Os 2 cenários passam
- [ ] Cobertura de ambos os arquivos atinge 100%
- [ ] `ruff check .` limpo
- [ ] Diretórios temporários são limpos após os testes

## Arquivos afetados

- `tests/test_jinja_template.py` (novo — ~40 linhas)
