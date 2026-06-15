# ISIS Report Codebase Architecture & Conventions

## Project Overview

**Project Name:** ISIS Report  
**Purpose:** A report generation API that creates HTML and PDF reports with flexible data aggregation, grouping, and templating capabilities. Reports support hierarchical grouping, summaries, and detail views.

**Description:** ISIS Report is a Python-based REST API for generating dynamic business reports from various data sources. It provides two main report types (Sections and Tabular) that can be rendered as HTML or PDF.

---

## Technology Stack

### Core Framework
- **Web Framework:** Robyn 0.2.x (async Python web framework)
- **OpenAPI:** Integrated OpenAPI support via `robyn.openapi`

### Key Dependencies
- **jinja2** - HTML/PDF template rendering with Jinja2 templating engine
- **pandas** - Data manipulation, grouping, and aggregation
- **playwright** - Headless Chromium browser for PDF generation
- **robyn** - Async Python web server

### Python Version
- **Requires:** Python 3.14+
- **Code Quality Tools:** Ruff (linting and formatting)

### Development & Deployment
- **Containerization:** Docker with uv package manager
- **Package Manager:** uv (Python package manager)
- **Environment:** Debian GNU/Linux 12 (bookworm)

---

## Project Structure

```
isis_report/
├── app/
│   ├── api/
│   │   └── __init__.py                    # Robyn app initialization & OpenAPI config
│   ├── constants.py                        # Global constants (paths, templates, margins)
│   ├── run.py                              # Entry point, module loader
│   ├── modules/                            # Feature modules (pluggable architecture)
│   │   ├── sections/                       # Sections report module
│   │   │   ├── __init__.py                # Module initialization
│   │   │   ├── router.py                  # SubRouter setup with /app/sections prefix
│   │   │   ├── models/
│   │   │   ├── routes/
│   │   │   │   └── sections.py            # POST /app/sections endpoint
│   │   │   └── services/
│   │   │       └── sections.py            # SectionsService: data retrieval, HTML/PDF generation
│   │   ├── tabular/                        # Tabular report module
│   │   │   ├── __init__.py
│   │   │   ├── router.py                  # SubRouter setup with /app/tabular prefix
│   │   │   ├── models/
│   │   │   │   └── tabular.py             # (Empty)
│   │   │   ├── routes/
│   │   │   │   └── tabular.py             # POST /app/tabular endpoint
│   │   │   └── services/
│   │   │       └── tabular.py             # TabularService: data retrieval, grouping, aggregation
│   │   └── status/                         # Health check module
│   │       ├── __init__.py
│   │       ├── router.py                  # SubRouter setup with /app/status prefix
│   │       ├── models/
│   │       │   └── status.py              # StatusResponse model
│   │       ├── routes/
│   │       │   └── status.py              # GET /app/status endpoint
│   │       └── services/
│   │           └── status.py              # StatusService: health check
│   ├── extensions/
│   │   ├── jinja_template/
│   │   │   ├── __init__.py                # render_template() function
│   │   │   └── templating.py              # JinjaTemplate & TemplateInterface
│   │   ├── log/
│   │   │   └── __init__.py                # basic_logger setup
│   │   └── routes_loader/
│   │       └── __init__.py                # Dynamic route loading
│   ├── ds/                                 # Data sources (mock data)
│   │   ├── calendar_semanal.py            # Weekly calendar data
│   │   ├── pedido_cartao.py               # Card request order data
│   │   ├── pedido_cartao_10.py            # (variants)
│   │   ├── pedido_cartao_11.py
│   │   ├── pedido_cartao_12.py
│   │   └── pedido_cartao.py
│   ├── templates/
│   │   ├── relatorio_base.j2              # Base template with blocks
│   │   ├── relatorio_sections_controller.j2   # Sections report layout
│   │   ├── relatorio_sections_fragments.j2    # Sections rendering macros
│   │   ├── relatorio_tabular_controller.j2    # Tabular report layout
│   │   └── relatorio_tabular_sections.j2      # Tabular rendering macros
│   └── logs/                               # Log files directory
├── dev/
│   └── dependencies.sh                    # Setup script
├── notes/
│   ├── calendario.json                    # Reference data
│   ├── group_logic.txt                    # Grouping logic documentation
│   ├── pedido_2.json
│   └── pedido.json
├── Dockerfile                             # Docker build config
├── dockercompose.yml                      # Docker Compose orchestration
├── pyproject.toml                         # Python project metadata & dependencies
└── README.md
```

---

## Architecture Patterns & Conventions

### 1. Module Architecture (Pluggable Pattern)

The application uses a **pluggable module architecture** where modules are auto-discovered and initialized:

- **Location:** `app/modules/`
- **Convention:** Each module is a directory containing:
  - `__init__.py` with `init_module(robyn_app: Robyn)` function
  - `router.py` with a `SubRouter` instance
  - `routes/` directory with route files
  - `services/` directory with business logic
  - `models/` directory with data models

**Module Initialization Flow (in run.py):**
```python
init_modules(app) → scans modules/ → loads __init__.py → calls init_module() → includes router
```

### 2. Request Flow

```
HTTP Request
    ↓
routes/{module}.py → Service.generate_report() 
    ↓
    ├── __obter_dados() → retrieves data from ds/ 
    ├── __tratar_dados() → processes/aggregates data (tabular only)
    ├── __gerar_html() → renders Jinja2 template
    └── __gerar_pdf() → (if type="pdf") Playwright HTML→PDF
    ↓
Response(description=content, status_code, headers)
```

### 3. Routing Convention

- **Base Path:** `/app` (from `constants.BASE_PATH`)
- **Module Prefixes:** 
  - Sections: `/app/sections` (POST)
  - Tabular: `/app/tabular` (POST)
  - Status: `/app/status` (GET)
- **SubRouter Pattern:** Each module creates a `SubRouter(prefix=f"{BASE_PATH}/{module_name}")`

### 4. Service Pattern

**Common Service Structure:**
```python
class XxxService:
    async def __obter_dados(self, payload/query) → list
    async def __tratar_dados(self, dados, config) → dict  # (tabular only)
    async def __gerar_html(self, dados, payload, layout) → str
    async def __gerar_pdf(self, html) → bytes
    async def generate_report(self, data: dict) → tuple(response, content_type)
```

**Conventions:**
- Double-underscore methods are private (Python convention)
- All methods are `async`
- Methods named with Portuguese Portuguese-English mix: `__obter_dados()`, `__gerar_html()`

### 5. Data Processing Pipeline

**Tabular Module (Advanced Grouping):**
The tabular service supports multi-level hierarchical grouping with aggregations:

1. **Data Retrieval:** `__obter_dados(query)` → returns list of dicts
2. **Data Processing:** `__tratar_dados()` performs:
   - Two-level grouping: `groupings.fields` (L1) + `groupings.groupings.fields` (L2)
   - Aggregations at each level via pandas `groupby()`
   - Summary calculations
   - Result structure: `{"groups": [...], "detail": [...], "summary": {...}}`

**Sections Module (Simple):**
- Mock data generation in `__obter_dados()`
- No aggregation; data passed directly to template

### 6. Template System

**Jinja2 with Custom Helpers:**
- Base template: `relatorio_base.j2`
- Controller templates extend base and import macros
- Macros in separate fragment files for rendering

**Naming Convention:**
- `relatorio_` prefix (means "report" in Portuguese)
- `_controller.j2` - main layout
- `_fragments.j2` or `_sections.j2` - macro definitions

**Available Context Variables:**
- `ds_items` - processed data
- `layout` - layout configuration from request
- `titulo` - report title
- `filters` - applied filters
- `zip` - Python zip function
- `fmt` - formatting function (locale-aware int/float/date)
- `mode` - render mode ("exact" default)
- `type` - report type ("html" or "pdf")
- `data_hora_impresssao` - print datetime

### 7. Formatting Function Pattern

**Locale-aware formatting in templates:**
```python
fmt(valor, mascara)
# mascara options: "int", "float", "date", "datetime"
```

### 8. PDF Generation

**Technology:** Playwright + Chromium
- Uses `async_playwright()` context manager
- Launches headless Chromium
- Converts HTML to PDF with:
  - Header/footer templates (from `constants.py`)
  - Page margins
  - A4 format

### 9. Response Pattern

**HTTP Responses:**
```python
Response(
    description=response_data,  # HTML string or PDF bytes
    status_code=200,
    headers={"Content-Type": "text/html" | "application/pdf"}
)
```

**Content Negotiation:** Based on `data.get("type")` → returns HTML or PDF

---

## Extension Architecture

### Jinja Template Extension
- **Location:** `app/extensions/jinja_template/`
- **Pattern:** Abstract interface + implementation
- **Initialization:** Singleton in `__init__.py` pointing to `app/templates/`
- **API:** `render_template(template_name: str, **context) → str`

### Logging Extension
- **Location:** `app/extensions/log/`
- **Pattern:** Singleton logger with file + console handlers
- **Feature:** Daily log rotation with timestamp in filename
- **Used:** Throughout app as `basic_logger`

### Routes Loader Extension
- **Location:** `app/extensions/routes_loader/`
- **Pattern:** Dynamic Python module loading
- **Function:** `init_routes(file)` → scans `routes/` directory and imports all `.py` files

---

## API Structure

### Endpoints

#### 1. **POST /app/sections** - Sections Report
**Request:**
```json
{
  "type": "html" | "pdf",
  "title": "Report Title",
  "layout": {...},
  "filters": {...},
  "sections": [...],
  "mode": "exact"
}
```
**Response:** HTML string or PDF bytes

#### 2. **POST /app/tabular** - Tabular Report
**Request:**
```json
{
  "type": "html" | "pdf",
  "title": "Report Title",
  "layout": {
    "detail": {...},
    "groups": {...},
    "summary": {...}
  },
  "filters": {...},
  "data_source": {
    "query": "1" | "2",
    "groupings": {
      "fields": ["field1", "field2"],
      "aggregations": ["field3", "field4"],
      "groupings": {
        "fields": ["field5"],
        "aggregations": ["field6"]
      }
    },
    "summary": ["field7"]
  }
}
```
**Response:** HTML string or PDF bytes

#### 3. **GET /app/status** - Health Check
**Response:**
```json
{
  "status": "healthy" | "unhealthy",
  "uptime": 12345.67,
  "error": "error message (optional)"
}
```

### OpenAPI Integration
- Integrated via `robyn.openapi`
- Routes decorated with `@router.get/post(..., openapi_name=..., openapi_tags=[...])`
- Auto-generated API documentation

---

## Data Models

### Status Response
```python
class StatusResponse(JSONResponse):
    status: str
    uptime: Optional[float] = None
```

### Tabular Data Structure
**After `__tratar_dados()`:**
```python
{
    "detail": [list of records],
    "groups": [
        {
            "field1": value,  # grouping field values
            "field3": aggregated_value,  # aggregations
            "groups": [  # sub-groups (2nd level)
                {
                    "field2": value,  # 2nd level grouping
                    "field6": aggregated_value,
                    "detail": [records]
                }
            ]
        }
    ],
    "summary": {
        "field7": sum_of_field7
    }
}
```

---

## Configuration & Constants

**File:** `app/constants.py`

```python
BASE_PATH = "/app"

HEADER_TEMPLATE = "<span>teste</span>"  # HTML for PDF header

FOOTER_TEMPLATE = """..."""  # HTML for PDF footer with page numbering

PAGE_MARGIN = {"top": ".2in", "bottom": ".5in"}
```

**Environment Variables (from docker-compose.yml):**
- `ROBYN_HOST` - Server host (default: 0.0.0.0)
- `ROBYN_PORT` - Server port (default: 8080)
- `ROBYN_LOG_LEVEL` - Robyn log level (default: WARN)
- `ROBYN_PROCESSES` - Number of processes (default: 5)
- `ROBYN_WORKERS` - Number of workers (default: 5)
- `TZ` - Timezone (default: America/Sao_Paulo)

---

## Data Sources

**Location:** `app/ds/`

Currently uses **static mock data** in Python dictionaries:

1. **calendario_semanal.py** - Weekly calendar (52 weeks of 2024)
2. **pedido_cartao.py** - Card order data with companies, products, tariffs

**Query Routing (in tabular service):**
- Query "1" → `ds_calendario`
- Query "2" → `ds_pedido`
- Query others → empty list

---

## Logging

**File:** `app/extensions/log/__init__.py`

**Configuration:**
- **Log Directory:** `{PROJECT_ROOT}/logs/`
- **Filename:** `log_YYYY_MM_DD.log` (daily rotation)
- **Format:** `%(asctime)s - %(levelname)s - %(name)s [%(filename)s; %(funcName)s; %(lineno)d] => %(message)s`
- **File Level:** DEBUG
- **Console Level:** INFO
- **Used as:** `from extensions.log import basic_logger`

---

## Project-Specific Conventions

### Naming Conventions
- **Module names:** snake_case, single word (sections, tabular, status)
- **Methods:** snake_case with Portuguese influence
  - `__obter_dados()` (private, "get data")
  - `__gerar_html()` (private, "generate HTML")
  - `__gerar_pdf()` (private, "generate PDF")
  - `__tratar_dados()` (private, "process data")
- **Templates:** `relatorio_` prefix + `_controller` / `_sections` / `_fragments` suffixes
- **Variables:** Portuguese-English mix (empresa, pedido, valor_total, etc.)

### Code Quality
- **Linter:** Ruff with rules: E, F, I, B, UP (excluding E501 line length)
- **Format:** Black-style with 140 char line length, double quotes
- **Target:** Python 3.14+

### Async Patterns
- All service methods are `async`
- Uses `async/await` exclusively
- Playwright uses `async_playwright()` context manager

### Error Handling
- Broad `except Exception:` blocks with logging (pylint-disabled)
- Return fallback values on error
- 500 status code with unhealthy status on error

### Type Hints
- Minimal type hints (not fully typed)
- Basic Python typing: `dict`, `list`, `str`, etc.
- Some use of `typing.Optional`

---

## Deployment

### Docker Setup
- **Base Image:** `ghcr.io/astral-sh/uv:python3.14-bookworm-slim`
- **Timezone:** America/Sao_Paulo
- **Browser:** Chromium via playwright (installed in image)
- **Health Check:** `curl -f http://localhost:8080/app/status`
- **Port:** 8080 (internal), 50002 (docker-compose external)

### Running the App
```bash
# Local development
python app/run.py

# With Robyn flags
python app/run.py --fast

# Docker
docker build -t isis_report .
docker-compose up
```

### Development Setup
```bash
# Install dependencies
uv sync
source .venv/bin/activate
playwright install chromium --with-deps --only-shell
```

---

## Key Differences from Common Patterns

1. **Portuguese-English Code Mix:** File names and core logic use English, but variables and method names use Portuguese
2. **Pluggable Modules:** Auto-discovery pattern rather than explicit registration
3. **Private Methods:** Extensive use of double-underscore private methods in services
4. **Direct HTML/PDF Response:** Reports returned as HTTP response body content (not file downloads)
5. **Async-First:** All I/O and template operations are async
6. **Singleton Services:** Services instantiated fresh per request (no singleton cache)
7. **Template-Driven Reports:** Report structure entirely driven by Jinja2 template layout definitions
8. **Multi-Level Grouping:** Tabular service supports arbitrary nesting levels with pandas groupby
9. **Locale-Aware Formatting:** Formatting functions use Python's locale module for number/date formatting
10. **Broad Exception Handling:** Catches all exceptions to prevent API crashes

---

## Development Workflow

1. **Add Module:** Create `modules/{module_name}/` with standard structure
2. **Define Routes:** Add route files in `modules/{module_name}/routes/`
3. **Implement Service:** Create service in `modules/{module_name}/services/`
4. **Create Templates:** Add Jinja2 templates to `app/templates/`
5. **Register Module:** Implement `init_module(robyn_app)` in `__init__.py`
6. **App Auto-loads:** `run.py` automatically discovers and initializes on startup

---

## Testing Strategies

- No unit tests present in codebase
- Manual testing via HTTP requests to endpoints
- Data validation done in services
- Error handling via try-except blocks

---

## Future Enhancement Opportunities

1. Add request validation using Pydantic models
2. Implement proper error handling with custom exceptions
3. Add unit/integration tests
4. Make data sources pluggable (database, API, file) instead of static
5. Add caching for frequently generated reports
6. Add report scheduling/background jobs
7. Implement user authentication/authorization
8. Add report template management UI

