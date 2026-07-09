# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt                    # Install deps
python -m main                                     # Run with hot reload (from backend/)
uvicorn main:app --host 0.0.0.0 --port 3001 --reload
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:3001  # Production
python tests/seed_test_data.py                     # Seed sample data
```

### Frontend (Vue 3)
```bash
cd frontend
npm install                                        # Install deps
npm run dev                                        # Dev server on :5173, proxies /api to :3001
npm run build                                      # Production build to frontend/dist/
npm run preview                                    # Preview production build
```

### Database
- **SQLite** (default): auto-created at `backend/storage/data/trade_flow.db`
- **MySQL**: set `DATABASE_TYPE=mysql` + `MYSQL_*` env vars; run `backend/sql/schema.sql`
- SQL schema: `backend/sql/schema.sql`, seed data: `backend/sql/seed.sql`

### Docker
```bash
docker-compose up -d                               # Deploy full stack (SQLite default)
docker build -t tradeflow .                        # Multi-stage build
```

### API Documentation
- Swagger UI: http://localhost:3001/docs
- ReDoc: http://localhost:3001/redoc

### Testing / Data Seeding
```bash
cd backend && python tests/seed_test_data.py       # Populates trades, positions, serial counters
```
No pytest/unit test framework is configured. Only manual seed-data scripts exist.

### Default Accounts
| Username | Password | Role |
|----------|----------|------|
| admin | admin | Admin |
| user001 | 123456 | User |

### GitHub Actions
- `.github/workflows/deploy.yml` builds frontend and deploys to GitHub Pages on push to main/master

## Architecture

**Grid trade tracking & portfolio analysis tool.** Full-stack SPA with RESTful API, DDD-layered backend.

```
Client (Vue 3 SPA) --HTTP/JSON--> FastAPI Backend --SQL--> SQLite / MySQL
                                       |
                                  Sina / Tencent / EastMoney
                                  (stock market data APIs, auto-failover)
```

### Layer Architecture (DDD)

The backend follows a four-layer Domain-Driven Design:

```
interfaces/          -- FastAPI routers + Pydantic schemas + middleware
  ↓
application/         -- Service layer (business logic orchestration)
  ↓
domain/              -- SQLAlchemy ORM models (entities)
  ↓
infrastructure/      -- DB engine, external API clients, scheduler, config
```

- **`interfaces/routers/`** — Thin route handlers: validate input, call services, return responses. (Exception: `trades.py` still has business logic in recalculate_position/generate_buy_order_no.)
- **`interfaces/schemas/`** — Pydantic request/response DTOs. Unified response wrapper: `ApiResponse { success, data, error }`.
- **`interfaces/middleware/`** — Global exception handler returning `ApiResponse` on 500s.
- **`interfaces/responses.py`** — `CharsetJSONResponse` ensures UTF-8 charset in JSON responses.
- **`application/services/`** — Business logic: auth, market data query, watchlist CRUD.
- **`domain/models/`** — SQLAlchemy ORM models with `fnos_` table prefix, re-exported from `__init__.py`.
- **`infrastructure/clients/`** — Stock data API providers: Sina → Tencent → EastMoney auto-failover chain.
- **`infrastructure/scheduler/`** — APScheduler: watchlist price refresh every 10 minutes.
- **`infrastructure/config.py`** — Env-based config (port, DB type/credentials).
- **`infrastructure/database.py`** — SQLAlchemy engine, SessionLocal, get_db() dependency, DeclarativeBase.

### Key Backend Files

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI app entry: lifespan (create tables, start/stop scheduler), router registration, static file serving, SPA fallback |
| `backend/app/infrastructure/config.py` | PORT, DATABASE_TYPE, DATABASE_URL construction |
| `backend/app/infrastructure/database.py` | SQLAlchemy engine + session factory |
| `backend/app/domain/models/*.py` | 9 ORM models (Stock, Trade, Position, User, Watchlist, etc.) |
| `backend/app/interfaces/routers/*.py` | 8 router modules under `/api/auth`, `/api/trades`, etc. |
| `backend/app/application/services/*.py` | 3 service modules (auth, market, watchlist) |
| `backend/app/infrastructure/clients/*.py` | 4 client modules (auto, sina, tencent, eastmoney) |
| `backend/app/infrastructure/scheduler/*.py` | APScheduler setup + watchlist refresh task |

### API Endpoints

All under `/api`:

| Prefix | Endpoints |
|--------|-----------|
| `/auth` | POST login, POST register, POST change-password, POST reset-password, GET users |
| `/trades` | GET list (grouped by buy_order_no), POST create (buy/sell), DELETE `/{id}` |
| `/positions` | GET list, PUT `/{id}/price` (update latest price), DELETE `/{id}` (clear + delete trades) |
| `/stocks` | GET `/search?q=&source=`, GET `/{code}`, POST `/batch` |
| `/watchlist` | GET list, POST add, DELETE `/{code}`, POST `/refresh` |
| `/trade-tags` | GET list, POST upsert, DELETE `/{id}` |
| `/portfolio` | GET list, POST create (accumulates price on duplicate contract), DELETE `/{id}` |
| `/contracts` | GET list, POST create, PUT `/{old_code}`, DELETE `/{code}` |

### Directory Structure

```
backend/
├── main.py                          # FastAPI entry point
├── app/
│   ├── domain/models/               # SQLAlchemy ORM models (9 models)
│   ├── application/services/        # Business logic (auth, market, watchlist)
│   ├── infrastructure/
│   │   ├── clients/                 # Stock data API clients (sina/tencent/eastmoney/auto)
│   │   ├── scheduler/              # APScheduler (watchlist refresh)
│   │   ├── config.py               # Env-based configuration
│   │   └── database.py             # SQLAlchemy engine + session
│   └── interfaces/
│       ├── routers/                # 8 FastAPI routers
│       ├── schemas/                # 10 Pydantic DTO modules
│       ├── middleware/             # Global exception handler
│       └── responses.py           # CharsetJSONResponse
├── sql/                            # schema.sql + seed.sql
├── storage/data/                   # SQLite database location
└── tests/                          # seed_test_data.py only
frontend/
├── src/
│   ├── api/
│   │   ├── http.js                 # Shared request wrapper (prepends /api, checks success)
│   │   ├── stock.js                # CRUD API calls (trades, positions, auth, portfolio, etc.)
│   │   └── stock-quote.js          # Market data API calls (search, quote, batch)
│   ├── stores/
│   │   ├── stock.js                # Main Pinia store (trades, positions, auth, modals, portfolio)
│   │   ├── stocks.js               # Stock search state
│   │   ├── watchlist.js            # Watchlist state (uses direct fetch(), not http.js)
│   │   ├── allocator2.js           # Portfolio allocator v2 (localStorage, ECharts treemap)
│   │   └── contract.js             # Contract CRUD state
│   ├── components/                 # Organized by domain
│   │   ├── auth/                   # LoginPage, ChangePasswordForm
│   │   ├── trade/                  # TradeList, PositionList, TradeModal, SellModal
│   │   ├── stocks/                 # StockSearch, SearchBar, StockCard, WatchlistPanel, etc.
│   │   ├── portfolio/              # PortfolioRatio, PortfolioAllocator2, PortfolioModal
│   │   ├── contract/               # ContractManagement
│   │   ├── admin/                  # UserManagement
│   │   ├── common/                 # ConfirmModal, Toast, DataTransfer, Dropdown
│   │   ├── layout/                 # Sidebar
│   │   └── sponsor/                # SponsorView
│   └── router/index.js             # Vue Router with 7 routes + Placeholder component
├── index.html
├── vite.config.js                  # Dev proxy /api -> :3001
├── tailwind.config.js
└── postcss.config.js
```

### Key Patterns & Conventions

- **Multi-tenancy via `user_id`**: All business tables have `user_id`. Frontend passes it as a query param on every API call. No auth middleware — backend trusts `user_id` from frontend. Admin role enforced only client-side.
- **Auth**: MD5+salt password hash, no JWT/sessions.
- **Unified response envelope**: All endpoints return `ApiResponse { success: bool, data: any, error: string }`.
- **Auto-generated order numbers**: `NOYYYYMMDDNNNN` via `fnos_serial_counters` table.
- **Position auto-recalculation**: Every trade create/delete triggers full recalculation of related positions.
- **Stock data failover chain**: Sina → Tencent → EastMoney; configurable via `source` query param.
- **Two portfolio systems**: v1 (`PortfolioRatio.vue`) and v2 (`PortfolioAllocator2.vue` with ECharts treemap, localStorage-backed).
- **All DB tables prefixed `fnos_`**.
- **Frontend stores connect to API modules**, not directly to `fetch()` (exception: `watchlist.js` uses direct `fetch()`).
- **Trade buy records use `remaining_shares`** to track unsold portion; sells decrement it.
- **Lazy data loading**: `App.vue` only loads trades/positions/tags on first visit to `home` route.

### Known Technical Debt

1. **`auto.py` sync/async mismatch** — `get_stocks()` and `search_stocks()` call `async` client functions without `await`. Also missing `get_stock()` singular. Needs full async rewrite.
2. **Inconsistent error responses** — Some routers return `ApiResponse(success=False)` while others `raise HTTPException(400)` (which returns `{"detail": "..."}`, breaking the frontend's `data.success` check).
3. **No CORS middleware** — Removed in the DDD refactor. Not an issue for single-deployment via `main.py` serving static files, but breaks split deployments.
4. **Duplicate `_d()` helper** — Defined in both `market.py` and `watchlist.py`.
5. **Business logic in routers** — `trades.py` has `recalculate_position()` and `generate_buy_order_no()` that belong in services.
6. **No automated tests** — Only `seed_test_data.py` exists; no pytest, unittest, or Vitest infrastructure.
7. **No linting/formatting config** — No eslint, prettier, ruff, flake8, or mypy config.
8. **Frontend `watchlist.js` uses `fetch()` directly** instead of the shared `http.js` wrapper.
