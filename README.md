# Event Discovery Service

Веб-платформа для поиска академических конференций, симпозиумов, воркшопов и call-for-papers (аналог WikiCFP). Backend на **FastAPI**, БД **PostgreSQL**, аутентификация **JWT**.

**Если при `docker-compose up` ошибка про `dockerDesktopLinuxEngine` или pipe** — Docker Desktop не запущен или не установлен. Запустите проект **без Docker**: см. [docs/RUN.md](docs/RUN.md), раздел «Вариант 2: Локально (без Docker)».

## Возможности

- Регистрация, вход, JWT, роли (user / admin)
- События: CRUD, поиск по ключевым словам, фильтры (категория, страна, город, режим, даты), сортировка, пагинация
- Категории: CRUD (админ), публичный список
- Избранное: добавить/удалить/список для текущего пользователя
- Админ: управление пользователями, событиями, категориями
- REST API с OpenAPI (Swagger / ReDoc)
- Health и readiness, метрики Prometheus
- Docker Compose, CI (GitHub Actions), тесты (pytest), нагрузочные тесты (k6)

## Стек

| Компонент   | Технология        |
|------------|-------------------|
| Backend    | FastAPI           |
| БД         | PostgreSQL 15     |
| ORM        | SQLAlchemy 2.0    |
| Миграции   | Alembic           |
| Auth       | JWT (python-jose), passlib/bcrypt |
| Валидация  | Pydantic          |
| Тесты      | pytest, pytest-asyncio, httpx |
| Нагрузка   | k6                |
| Контейнеры | Docker, docker-compose |
| CI         | GitHub Actions    |
| Мониторинг | Prometheus, Grafana |

## Быстрый старт

```bash
# Клонировать и перейти в каталог
git clone https://github.com/zhanel7/event-discovery-wikicfp.git
cd event-discovery-wikicfp

# Запуск через Docker
docker-compose up --build
```

После запуска:

- API и документация: http://localhost:8000/api/docs  
- Health: http://localhost:8000/health  
- Метрики: http://localhost:8000/metrics  

Опционально — заполнить БД тестовыми данными (админ + категории):

```bash
docker-compose exec api python scripts/seed_data.py
# Логин админа: admin / admin123
```

Подробные шаги (локальный запуск без Docker, тесты, k6) — в **[docs/RUN.md](docs/RUN.md)**.

## Структура проекта

```
app/                 # FastAPI-приложение
  api/v1/endpoints/  # Эндпоинты (auth, users, events, categories, favorites, admin)
  core/              # Конфиг, безопасность, исключения, логирование
  db/                # Сессия БД
  models/            # SQLAlchemy-модели
  schemas/           # Pydantic-схемы
  services/          # Бизнес-логика
  repositories/      # Доступ к данным
  middleware/        # Метрики Prometheus
alembic/             # Миграции
tests/               # pytest
scripts/             # seed_data.py, k6_load_events.js
docs/                # ARCHITECTURE.md, RUN.md
```

## API (кратко)

| Метод | Путь | Описание |
|-------|------|----------|
| POST | /api/v1/auth/register | Регистрация |
| POST | /api/v1/auth/login | Вход (JWT) |
| GET | /api/v1/users/me | Профиль (auth) |
| GET | /api/v1/events | Список событий (поиск, фильтры, пагинация) |
| GET | /api/v1/events/{id\|slug} | Детали события |
| POST | /api/v1/events | Создать событие (admin) |
| PATCH/DELETE | /api/v1/events/{id} | Обновить/удалить (admin) |
| GET | /api/v1/categories | Список категорий |
| CRUD | /api/v1/categories | Категории (admin) |
| GET/POST/DELETE | /api/v1/favorites | Избранное (auth) |
| GET | /api/v1/admin/users | Список пользователей (admin) |
| GET | /health, /health/ready | Liveness / readiness |
| GET | /metrics | Prometheus-метрики |

## Тесты и k6

```bash
# Создать БД для тестов
createdb eventdb_test

# Запуск тестов
pytest tests/ -v

# Нагрузочный тест (k6)
k6 run -e BASE_URL=http://localhost:8000 scripts/k6_load_events.js
```

## Переменные окружения

См. `.env.example`. Основные:

- `SECRET_KEY` — секрет для JWT (обязательно в production)
- `DATABASE_URL` — PostgreSQL (async): `postgresql+asyncpg://user:pass@host:5432/dbname`
- `DATABASE_URL_SYNC` — для Alembic: `postgresql://user:pass@host:5432/dbname`

## Документация

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — архитектура, схема БД, API
- [docs/RUN.md](docs/RUN.md) — как запустить (Docker и локально), тесты, k6

## Лицензия

По условиям репозитория/курса.
