# Oxilière HR 🧑‍💼

> **Human Resource Management System** — A modern, multi-tenant HR platform built with Django Ninja (backend) and SvelteKit (frontend).

Oxilière HR is a full-featured HR management system designed for African enterprises, with multi-tenant architecture, event-driven messaging, and a rich, responsive UI. It manages the complete employee lifecycle from recruitment to payroll.

---

## ✨ Features

| Module           | Description |
|------------------|-------------|
| **Employees**    | Manage employee records, contracts, documents, and the full employment lifecycle |
| **Recruitment**  | Job postings, applications, candidate tracking, and hiring pipelines |
| **Leaves**       | Leave requests, approvals, balances, and policy enforcement |
| **Attendance**   | Time tracking, check-in/out, attendance reports and analytics |
| **Payroll**      | Salary processing, benefits, deductions, and payslip generation |
| **Jobs & Positions** | Job definitions, position management, and organizational structure |
| **Banking**      | Employee bank account management and payment information |
| **Calendar**     | Events, scheduling, and company-wide calendar management |
| **Performance**  | Reviews, goals, evaluations, and performance tracking |

---

## 🏗️ Architecture

```
oxiliere_hr/
├── backend/                  # Django + Ninja API
│   ├── hr/                   # HR app (10 modules)
│   │   ├── employees/
│   │   ├── recruitment/
│   │   ├── leaves/
│   │   ├── attendance/
│   │   ├── payroll/
│   │   ├── jobs/
│   │   ├── banking/
│   │   ├── calendar/
│   │   └── performance/
│   ├── ox_hr/                # Project configuration
│   │   └── settings/         # Modular settings (base, apps, databases, etc.)
│   ├── core/                 # Shared core functionality
│   └── main.py
│
├── frontend/                 # SvelteKit UI
│   └── src/
│       ├── lib/
│       │   ├── features/     # Feature modules (mirrors backend)
│       │   ├── api/          # API client layer (Axios + TanStack Query)
│       │   ├── components/   # UI & shared components
│       │   ├── stores/       # Svelte 5 reactive stores
│       │   ├── hooks/        # Custom hooks
│       │   └── types/        # TypeScript type definitions
│       └── routes/           # SvelteKit pages & layouts
│
└── package.json              # Root workspace config
```

### 🧩 Key Technologies

**Backend**
- [Python](https://python.org) 3.12+ — Core language
- [Django](https://djangoproject.com) 5.2 — Web framework
- [Django Ninja Extra](https://eadwincode.github.io/django-ninja-extra) — REST API with controllers
- [Django Ninja JWT](https://github.com/eadwinCode/django-ninja-jwt) — JWT authentication
- [django-tenants](https://django-tenants.readthedocs.io) — Multi-tenancy (schema-based)
- [PostgreSQL](https://postgresql.org) — Primary database
- [Redis](https://redis.io) — Caching (CacheOps) & Celery broker
- [Celery](https://docs.celeryq.dev) — Async task queue
- [django-money](https://github.com/django-money/django-money) — Multi-currency support
- [django-safedelete](https://github.com/mbourqui/django-safedelete) — Soft delete
- [django-auditlog](https://github.com/jazzband/django-auditlog) — Audit trail
- [Pydantic](https://docs.pydantic.dev) — Data validation & serialization

**Frontend**
- [Svelte](https://svelte.dev) 5 — UI framework (runes & snippets)
- [SvelteKit](https://kit.svelte.dev) 2 — Full-stack framework
- [TypeScript](https://typescriptlang.org) 5 — Type safety
- [TailwindCSS](https://tailwindcss.com) 4 — Utility-first styling
- [TanStack Query](https://tanstack.com/query/latest) — Server state management
- [TanStack Form](https://tanstack.com/form/latest) — Form management
- [Axios](https://axios-http.com) — HTTP client
- [Chart.js](https://chartjs.org) — Data visualization
- [Lucide](https://lucide.dev) — Icons
- [Zod](https://zod.dev) — Schema validation
- [bits-ui](https://bits-ui.com) — Headless UI primitives
- [mode-watcher](https://mode-watcher.vercel.app) — Dark/light mode
- [DnD Kit](https://dndkit.com) — Drag & drop

---

## 🚀 Getting Started

### Prerequisites

| Tool       | Version |
|------------|---------|
| Python     | ≥ 3.12  |
| Node.js    | ≥ 20    |
| pnpm       | ≥ 9     |
| PostgreSQL | ≥ 15    |
| Redis      | ≥ 7     |

### 1. Clone & Install

```bash
# Clone the repository
git clone <repository-url>
cd oxiliere_hr

# Backend — using uv (recommended) or pip
cd backend
uv sync          # Install Python dependencies
# or: pip install -e .

# Frontend — using pnpm
cd ../frontend
pnpm install
```

### 2. Environment Configuration

Each environment requires its own `.env` file:

**Backend** (`backend/.env`):
```env
DJANGO_SETTINGS_MODULE=ox_hr.settings.local
DATABASE_URL=postgresql://user:password@localhost:5432/oxiliere_hr
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
```

**Frontend** (`frontend/.env`):
```env
PUBLIC_API_BASE_URL=http://localhost:8000/api
```

### 3. Run Database Migrations

```bash
cd backend
uv run python manage.py migrate_schemas  # Multi-tenant migrations
```

### 4. Start Development Servers

```bash
# Terminal 1 — Backend API
cd backend
uv run python manage.py runserver

# Terminal 2 — Frontend dev server
cd frontend
pnpm dev
```

The API will be available at `http://localhost:8000/api/docs` (Swagger UI) and the frontend at `http://localhost:5173`.

---

## 🧪 Development

### Backend Commands

```bash
cd backend
uv run python manage.py makemigrations   # Create migrations
uv run python manage.py migrate_schemas  # Apply migrations
uv run python manage.py createsuperuser  # Create admin user
uv run python manage.py test             # Run tests
```

### Frontend Commands

```bash
cd frontend
pnpm dev          # Start dev server
pnpm build        # Production build
pnpm preview      # Preview production build
pnpm check        # Type-check with svelte-check
pnpm lint         # Lint (ESLint + Prettier)
pnpm format       # Format code (Prettier)
```

---

## 🔌 API Overview

The API is built with **Django Ninja Extra** (controllers pattern) and automatically generates interactive OpenAPI documentation.

| Endpoint              | Description          |
|-----------------------|----------------------|
| `/api/docs`           | Swagger UI           |
| `/api/employees/...`  | Employee management  |
| `/api/recruitment/...`| Recruitment pipeline |
| `/api/leaves/...`     | Leave management     |
| `/api/payroll/...`    | Payroll processing   |

---

## 🌍 Localization

The application supports internationalization with Django's i18n framework. Translation files are located in `backend/locale/` and `backend/hr/locale/`.

```bash
cd backend
uv run django-admin compilemessages  # Compile .po → .mo
```

---

## 📦 Project Scripts

A root `package.json` with shared dependencies (`qs`) is available at the monorepo root for common utilities.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
