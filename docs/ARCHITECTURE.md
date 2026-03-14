# Event Discovery Service — Architecture & Design

## 1. Architecture Overview

The system follows a **layered clean architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│  Client (Browser / API consumers)                                │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Reverse Proxy (Nginx, optional)                                 │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  API Layer (FastAPI routers, request/response schemas)           │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Service Layer (business logic, orchestration)                   │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Repository Layer (data access, queries)                         │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Database (PostgreSQL)                                            │
└─────────────────────────────────────────────────────────────────┘
```

- **API**: HTTP endpoints, validation (Pydantic), auth dependency.
- **Services**: Use-case logic, no HTTP; depend on repositories and core.
- **Repositories**: CRUD and query logic; depend only on models and DB session.
- **Core**: Config, security (JWT, password hashing), exceptions, logging.

## 2. Folder Structure

```
app/
├── __init__.py
├── main.py                    # FastAPI app entry
├── api/
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       ├── router.py          # Aggregates all v1 routes
│       └── endpoints/
│           ├── __init__.py
│           ├── auth.py
│           ├── users.py
│           ├── events.py
│           ├── categories.py
│           ├── favorites.py
│           └── admin.py
├── core/
│   ├── __init__.py
│   ├── config.py              # Settings from env
│   ├── security.py            # JWT, password hashing
│   ├── exceptions.py          # Custom exceptions and handlers
│   └── logging.py             # Structured logging
├── db/
│   ├── __init__.py
│   ├── session.py             # Session factory, dependency
│   └── base.py                # Declarative base
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── event.py
│   ├── category.py
│   ├── favorite.py
│   └── event_category.py     # Association table
├── schemas/
│   ├── __init__.py
│   ├── common.py              # Pagination, error responses
│   ├── auth.py
│   ├── user.py
│   ├── event.py
│   ├── category.py
│   └── favorite.py
├── services/
│   ├── __init__.py
│   ├── auth.py
│   ├── user.py
│   ├── event.py
│   ├── category.py
│   └── favorite.py
├── repositories/
│   ├── __init__.py
│   ├── user.py
│   ├── event.py
│   ├── category.py
│   └── favorite.py
├── middleware/
│   ├── __init__.py
│   ├── logging.py
│   └── request_id.py
└── utils/
    ├── __init__.py
    └── slug.py

alembic/                        # Migrations
tests/                          # pytest
scripts/                        # Seed, k6
```

## 3. Database Schema (ER Diagram)

```mermaid
erDiagram
    users ||--o{ events : creates
    users ||--o{ favorites : has
    events ||--o{ event_categories : has
    categories ||--o{ event_categories : has
    events }o--|| users : created_by

    users {
        uuid id PK
        string username UK
        string email UK
        string hashed_password
        string role
        bool is_active
        datetime created_at
        datetime updated_at
    }

    events {
        uuid id PK
        string title
        string slug UK
        text short_description
        text full_description
        string organizer
        string country
        string city
        string venue
        string mode
        date start_date
        date end_date
        date submission_deadline
        date notification_deadline
        date camera_ready_deadline
        string website_url
        string cfp_url
        string image_url
        string status
        uuid created_by FK
        datetime created_at
        datetime updated_at
    }

    categories {
        uuid id PK
        string name
        string slug UK
        text description
        datetime created_at
        datetime updated_at
    }

    event_categories {
        uuid event_id FK
        uuid category_id FK
        PK (event_id, category_id)
    }

    favorites {
        uuid id PK
        uuid user_id FK
        uuid event_id FK
        datetime created_at
        UK (user_id, event_id)
    }
```

### Entity Summary

| Entity | Purpose |
|--------|--------|
| **User** | Auth, profile, role (user/admin), creator of events. |
| **Event** | Conference/workshop/symposium; slug for URLs; status draft/published/archived. |
| **Category** | Topic/domain (e.g. ML, NLP); many-to-many with Event. |
| **EventCategory** | Association table Event ↔ Category. |
| **Favorite** | User bookmarks; unique (user_id, event_id). |

### Indexes (for performance)

- `events(slug)` UNIQUE
- `events(start_date)`, `events(submission_deadline)`, `events(status)`, `events(mode)`, `events(country)`, `events(created_at)`
- `categories(slug)` UNIQUE
- `favorites(user_id)`, `favorites(user_id, event_id)` UNIQUE
- Full-text or GIN on `events(title, short_description)` if needed

## 4. API Design Summary

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/register` | No | Register |
| POST | `/api/v1/auth/login` | No | Login (returns access token) |
| GET | `/api/v1/users/me` | JWT | Current user profile |
| PATCH | `/api/v1/users/me` | JWT | Update profile |
| GET | `/api/v1/events` | No | List events (search, filter, sort, paginate) |
| GET | `/api/v1/events/{id_or_slug}` | No | Event detail |
| POST | `/api/v1/events` | JWT Admin | Create event |
| PATCH | `/api/v1/events/{id}` | JWT Admin | Update event |
| DELETE | `/api/v1/events/{id}` | JWT Admin | Delete event |
| GET | `/api/v1/categories` | No | List categories |
| GET | `/api/v1/categories/{id_or_slug}` | No | Category detail |
| POST | `/api/v1/categories` | JWT Admin | Create category |
| PATCH | `/api/v1/categories/{id}` | JWT Admin | Update category |
| DELETE | `/api/v1/categories/{id}` | JWT Admin | Delete category |
| GET | `/api/v1/favorites` | JWT | List current user favorites |
| POST | `/api/v1/favorites` | JWT | Add favorite (body: event_id) |
| DELETE | `/api/v1/favorites/{event_id}` | JWT | Remove favorite |
| GET | `/api/v1/admin/users` | JWT Admin | List users |
| GET | `/health` | No | Liveness |
| GET | `/health/ready` | No | Readiness (DB) |
| GET | `/metrics` | No | Prometheus metrics (optional) |

### Query Parameters for `GET /api/v1/events`

- `q` / `search`: keyword (title, description)
- `category` / `category_id`: filter by category
- `country`, `city`: location
- `mode`: online | offline | hybrid
- `status`: draft | published | archived (admin may see draft)
- `start_date_from`, `start_date_to`: event date range
- `submission_deadline_from`, `submission_deadline_to`: CFP deadline range
- `sort`: start_date | submission_deadline | created_at | title
- `order`: asc | desc
- `page`, `page_size`: pagination

### Response Conventions

- Success: `{ "data": T }` or list with `{ "items": [], "total": N, "page": P, "page_size": S }`
- Errors: `{ "detail": string or list of errors }` with appropriate HTTP status (400, 401, 403, 404, 409, 422, 500)

## 5. Implementation Roadmap

| Phase | Tasks |
|-------|--------|
| **1. Foundation** | Project scaffold, config, logging, DB session, Alembic, base exceptions |
| **2. Domain & DB** | SQLAlchemy models (User, Event, Category, Favorite, EventCategory), migrations, indexes |
| **3. Auth** | JWT (access token), password hashing, register/login, dependency `get_current_user`, role check |
| **4. Users** | GET/PATCH `/users/me`, schemas |
| **5. Categories** | CRUD, repositories, services, public list/detail |
| **6. Events** | CRUD, search/filter/sort/pagination, slug resolution, admin-only create/update/delete |
| **7. Favorites** | Add/remove/list favorites (user-scoped) |
| **8. Admin** | Admin-only endpoints (e.g. list users), optional moderation |
| **9. Non-functional** | Error handlers, request ID, health/ready, optional metrics, rate-limit proposal |
| **10. Quality** | pytest (unit + integration), k6 script, Docker, CI/CD, docs (README, API table, ER, deployment) |

---

This document is the single source of truth for architecture, schema, and API design. Implementation follows this plan in order.
