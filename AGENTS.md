# AI Agent Guide for ISIS Report

**Project:** ISIS Report - Python async REST API for generating HTML/PDF business reports  
**Tech Stack:** Python 3.14+, Robyn, Jinja2, Pandas, Playwright, Docker

---

## Quick Start for Agents

### Entry Point
```bash
cd /workspaces/isis_report
python app/run.py
```
API runs on `http://localhost:8080` with auto-reloading (development mode)

### Key Files to Know
- **[CODEBASE_ARCHITECTURE.md](CODEBASE_ARCHITECTURE.md)** - Complete technical reference (400+ lines)
- **[app/run.py](app/run.py)** - Application entry point & module loader
- **[app/modules/](app/modules/)** - Feature modules (sections, tabular, status)
- **[app/extensions/](app/extensions/)** - Robyn extensions (templating, logging, route loading)
- **[app/templates/](app/templates/)** - Jinja2 templates for reports

---

## Project Architecture

### Pluggable Module System
Each feature is a self-contained module with predictable structure:

```
app/modules/{module_name}/
├── __init__.py              # Must export init_module(robyn_app) function
├── router.py                # SubRouter(prefix=f"/app/{module_name}")
├── routes/
│   └── {module_name}.py     # @get or @post endpoints
├── services/
│   └── {module_name}.py     # Business logic (data retrieval, processing, rendering)
└── models/                  # Pydantic/data models
```

**To add a new module:** Follow this pattern and it will auto-discover.

### Three Main Endpoints

| Endpoint | Method | Purpose | Module |
|----------|--------|---------|--------|
| `/app/sections` | POST | Section-based reports (simple) | `modules/sections/` |
| `/app/tabular` | POST | Tabular reports (grouping, aggregations) | `modules/tabular/` |
| `/app/status` | GET | Health check | `modules/status/` |

---

## Key Conventions & Patterns

### 1. **Async-First Design**
- All I/O and template rendering operations are async
- Use `async def` for all service methods and route handlers
- All file operations use async methods where available

### 2. **Service Pattern**
Services follow a consistent private method pattern:
```python
class ReportService:
    async def generate_report(self, params, report_type):
        data = await self.__obter_dados()              # Retrieve data
        processed = await self.__tratar_dados(data)     # Process/aggregate
        html = await self.__gerar_html(processed)       # Render template
        if report_type == "pdf":
            return await self.__gerar_pdf(html)         # Convert to PDF
        return html
```

**Convention:** Private methods use `__double_underscore` prefix (name mangling).

### 3. **Template Rendering**
- **Engine:** Jinja2 (configured in `app/extensions/jinja_template/`)
- **Location:** All `.j2` files in `app/templates/`
- **Pattern:** 
  - Base templates (`relatorio_base.j2`) define blocks
  - Controller templates extend base and define layout
  - Fragment templates (`*_fragments.j2`) contain macros for rendering data
- **Custom context variables:** `layout`, `filters`, `fmt()` function for locale-aware formatting

### 4. **PDF Generation**
- Uses **Playwright with Chromium**
- Configuration in `app/constants.py` (margins, page sizes)
- Service methods: `await self.__gerar_pdf(html_content)` returns bytes
- Response headers: `Content-Type: application/pdf`, `Content-Disposition: attachment`

### 5. **Data Sources**
Mock data located in `app/ds/`:
- `calendario_semanal.py` - Weekly calendar data
- `pedido_cartao*.py` - Card request order variants
Used for testing without external dependencies.

### 6. **Language Mix**
- **Code:** English filenames and classes
- **Methods:** Portuguese names (`__obter_dados`, `__tratar_dados`, etc.)
- **Documentation:** Bilingual (English code comments, Portuguese user-facing text)

---

## Development Workflow

### Code Quality
```bash
# Linting with Ruff
ruff check app/

# Formatting with Ruff
ruff format app/

# Configuration in pyproject.toml
# - Line length: 140 characters
# - Target Python: 3.14
# - Selected rules: E, F, I, B, UP
```

### Logging
- Daily rotating logs in `app/logs/`
- Logger configured via `app/extensions/log/`
- Use: `from app.extensions.log import logger`

### Testing Approach
- Mock data in `app/ds/` provides test fixtures
- Send POST requests to endpoints with sample payloads
- Check response HTML/PDF output

---

## Common Tasks & Patterns

### Adding a New Report Type
1. Create directory: `app/modules/{new_report}/`
2. Copy structure from `app/modules/sections/` or `app/modules/tabular/`
3. Implement `init_module()`, `router`, routes, services
4. Create templates in `app/templates/relatorio_{new_report}_*.j2`
5. API auto-discovers and registers routes

### Modifying Report Output
1. **Layout changes:** Edit controller templates (`relatorio_*_controller.j2`)
2. **Data rendering:** Edit fragment templates (`relatorio_*_fragments.j2`)
3. **Processing logic:** Edit service methods in `app/modules/{module}/services/`

### Adding Report Grouping Logic
- **Location:** `app/modules/tabular/services/tabular.py`
- **Method:** `__tratar_dados()` uses Pandas `groupby()`
- **Reference:** See `app/notes/group_logic.txt` for grouping specifications

### Response Format
Services return `Response` objects:
```python
Response(
    description=html_or_pdf_bytes,
    status_code=200,
    headers={"Content-Type": "text/html; charset=utf-8"}  # or application/pdf
)
```

---

## Docker & Deployment

### Build & Run
```bash
# Using Docker Compose
docker-compose up --build

# Build Dockerfile
docker build -t isis-report .
docker run -p 8080:8080 isis-report
```

### Package Manager
- **Uses:** `uv` (not pip) for reproducible dependency management
- **Config:** `pyproject.toml`
- **Lock file:** `uv.lock` (auto-generated)

---

## Important Pitfalls

1. **Request handler signatures:** Always use correct `async def` signature with positional params for body data
2. **Template context:** Ensure all variables passed to template exist; Jinja2 errors halt rendering
3. **PDF generation:** Requires Chromium; ensure browser state is clean between requests
4. **Module discovery:** `init_module()` must be defined in `__init__.py` or module won't load
5. **Async/await:** Missing `await` on async calls will fail at runtime

---

## References & Links

- **Full Architecture:** [CODEBASE_ARCHITECTURE.md](CODEBASE_ARCHITECTURE.md)
- **Robyn Docs:** https://docs.robyn.io/
- **Jinja2 Docs:** https://jinja.palletsprojects.com/
- **Pandas Groupby:** https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html

---

*Generated for AI coding agents. Update this file as conventions evolve.*
