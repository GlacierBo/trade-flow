# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt          # Install deps
python -m app.main                       # Run with hot reload
uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload   # Alternative
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:3001  # Production
python seed_test_data.py                 # Seed sample data (creates admin/admin and user001/123456)
```

### Frontend (Vue 3)
```bash
cd frontend
npm install                              # Install deps
npm run dev                              # Dev server on :5173, proxies /api to :3001
npm run build                            # Production build to frontend/dist/
npm run preview                          # Preview production build
```

### Database
- **SQLite** (default, zero-config): auto-created at `../data/trade_flow.db` on first run
- **MySQL**: set `DATABASE_TYPE=mysql` in env, run `backend/sql/schema.sql` to init tables
- SQL schema: `backend/sql/schema.sql`, seed data: `backend/sql/seed.sql`

### Docker
```bash
docker-compose up -d                     # Deploy full stack (SQLite default)
docker build -t tradeflow .              # Multi-stage build
```

### API Documentation
- Swagger UI: http://localhost:3001/docs
- ReDoc: http://localhost:3001/redoc

## Architecture

**Grid trade tracking & portfolio analysis tool.** Full-stack SPA with RESTful API.

```
Client (Vue 3 SPA) --HTTP/JSON--> FastAPI Backend --SQL--> SQLite / MySQL
                                       |
                                  Sina / Tencent / EastMoney
                                  (stock market data APIs)
```

### Key patterns

- **Multi-tenancy via `user_id`**: All business tables (`fnos_trades`, `fnos_positions`, `fnos_portfolio_items`, `fnos_trade_tags`, `fnos_contracts`) have a `user_id` column. Every query filters by it. The frontend passes `user_id` as a query parameter on every request.
- **Auth**: Simple MD5+salt password hash. No JWT/sessions — the server trusts the `user_id` from the frontend. Admin role is enforced only on the frontend, not server-side.
- **Auto-generated order numbers**: `fnos_serial_counters` table generates sequential order numbers in format `NOYYYYMMDDNNNN`.
- **Position auto-recalculation**: Every trade create/delete triggers full recalculation of related positions (avg cost, profit, shares).
- **Stock data sources**: Auto-failover chain: Sina → Tencent → EastMoney (see `backend/clients/auto.py`).
- **Watchlist refresh**: APScheduler auto-refreshes watchlist prices every 10 minutes.
- **Two portfolio allocation systems**: v1 (`allocator.js`) and v2 (`allocator2.js` with ECharts treemap), both localStorage-based.

### Directory structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI app entry, CORS, router registration
│   ├── config.py                # Env-based config (DB type, paths, credentials)
│   ├── database.py              # SQLAlchemy engine + session factory
│   ├── models/                  # SQLAlchemy ORM models (one file per table)
│   ├── schemas/                 # Pydantic request/response DTOs
│   ├── routers/                 # Route handlers (thin — validation only)
│   ├── services/                # Business logic layer
│   ├── middleware/              # Exception handlers
│   └── scheduler/              # APScheduler (watchlist refresh)
├── clients/                     # Stock data API clients with auto-failover
├── sql/                         # schema.sql + seed.sql
└── seed_test_data.py           # Test data generator
frontend/
├── src/
│   ├── api/                     # HTTP calls (stock.js for CRUD, stock-quote.js for market data)
│   ├── stores/                  # Pinia state stores (one per domain)
│   ├── components/              # Organized by domain: auth/, trade/, stocks/, portfolio/, contract/, admin/
│   └── router/index.js          # Vue Router with 7 routes
└── vite.config.js               # Dev proxy /api -> :3001
```

### API endpoints

All under `/api`, grouped by router:
- **`/auth`** — login, register, change/reset password, user list
- **`/trades`** — CRUD trades (buy/sell with auto profit calculation)
- **`/positions`** — list positions, update price, delete (clears related trades)
- **`/stocks`** — search stocks, batch quotes, single quote
- **`/watchlist`** — CRUD watchlist, refresh prices
- **`/trade-tags`** — quick-trade tag shortcuts
- **`/portfolio`** — portfolio items (accumulates price on duplicate contract)
- **`/contracts`** — contract CRUD

### Default accounts
| Username | Password | Role |
|----------|----------|------|
| admin | admin | Admin |
| user001 | 123456 | User |

### Conventions
- All database tables prefixed with `fnos_`
- Backend layer separation: `routers/` (HTTP handling) → `services/` (business logic) → `models/` (ORM)
- Stock data clients live in `backend/clients/`, not in `app/`
- Frontend stores connect to API modules, not directly to fetch()
- Trade buy records use `remaining_shares` to track unsold portion; sells decrement it
