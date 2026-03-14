# Как запустить Event Discovery Service (FastAPI)

---

## ⚠ Если ошибка Docker: "pipe dockerDesktopLinuxEngine / The system cannot find the file specified"

Это значит, что **Docker Desktop не запущен** или не установлен. Варианты:

1. **Запустить Docker Desktop** (Пуск → Docker Desktop) и подождать, пока он **полностью** загрузится (иконка кита в трее, без «Starting...»). Затем снова: `docker-compose up --build`. Если образы не тянутся — проверьте интернет и при необходимости используйте минимальный вариант: `docker-compose -f docker-compose.minimal.yml up --build` (только API + PostgreSQL).

2. **Запустить без Docker** — см. раздел **«Вариант 2: Локально (без Docker)»** ниже. Нужны только Python 3.11+ и PostgreSQL.

---

## Вариант 1: Docker Compose

Нужны **Docker Desktop** и **Docker Compose** (входят в Docker Desktop).

1. Перейдите в каталог проекта:
   ```bash
   cd event-discovery-wikicfp
   ```

2. (Опционально) Создайте `.env` из примера и при необходимости задайте `SECRET_KEY`:
   ```bash
   cp .env.example .env
   ```

3. Запустите все сервисы:
   ```bash
   docker-compose up --build
   ```
   При первом запуске собирается образ API, выполняются миграции Alembic, затем запускается сервер.

4. Откройте в браузере:
   - **Swagger UI:** http://localhost:8000/api/docs  
   - **ReDoc:** http://localhost:8000/api/redoc  
   - **Health:** http://localhost:8000/health  
   - **Metrics (Prometheus):** http://localhost:8000/metrics  

   Сервисы: PostgreSQL — порт **5432**, Prometheus — **9090**, Grafana — **3000**.

5. (Опционально) Наполнить БД тестовыми категориями и админом:
   ```bash
   docker-compose exec api python scripts/seed_data.py
   ```
   Будет создан пользователь **admin** / **admin123** и несколько категорий (Machine Learning, NLP и др.). Для скрипта внутри контейнера уже заданы `DATABASE_URL` и окружение.

---

## Вариант 2: Локально (без Docker) — если Docker не работает

Подойдёт, если Docker выдаёт ошибку с `dockerDesktopLinuxEngine` или его нет.

### Шаг 1: Установить PostgreSQL

- Скачайте с https://www.postgresql.org/download/windows/ и установите (порт 5432, запомните пароль пользователя `postgres`).
- Либо используйте уже установленный PostgreSQL.

### Шаг 2: Создать базу данных

Откройте **pgAdmin** или командную строку PostgreSQL и выполните:

```sql
CREATE DATABASE eventdb;
```

(Если подключаетесь через `psql`: `psql -U postgres`, затем `CREATE DATABASE eventdb;`.)

### Шаг 3: Python и зависимости

В корне проекта (где лежит `requirements.txt`):

```bash
cd event-discovery-wikicfp
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

(На Linux/macOS: `source venv/bin/activate`.)

### Шаг 4: Файл `.env`

В корне проекта создайте файл `.env` (скопируйте из `.env.example` или создайте вручную) с содержимым:

```
SECRET_KEY=my-secret-key-at-least-32-characters-long
DATABASE_URL=postgresql+asyncpg://postgres:ВАШ_ПАРОЛЬ@localhost:5432/eventdb
DATABASE_URL_SYNC=postgresql://postgres:ВАШ_ПАРОЛЬ@localhost:5432/eventdb
```

Замените `ВАШ_ПАРОЛЬ` на пароль пользователя `postgres`. Если пользователь другой — замените и его в URL.

### Шаг 5: Миграции

```bash
alembic upgrade head
```

### Шаг 6: (По желанию) Тестовые данные

```bash
python scripts/seed_data.py
```

Будет создан админ **admin** / **admin123** и категории.

### Шаг 7: Запуск сервера

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Откройте в браузере: **http://localhost:8000/api/docs**

---

## Тесты

- Создайте тестовую БД (для локального запуска тестов):
  ```sql
  CREATE DATABASE eventdb_test;
  ```
- Установите зависимости (уже в `requirements.txt`).
- Запуск:
  ```bash
  pytest tests/ -v
  ```
  В CI используется переменная `DATABASE_URL` для подключения к `eventdb_test`.

---

## Нагрузочное тестирование (k6)

Установите [k6](https://k6.io/docs/get-started/installation/), затем:

```bash
k6 run scripts/k6_load_events.js
```

С другим хостом (например, после `docker-compose up`):

```bash
k6 run -e BASE_URL=http://localhost:8000 scripts/k6_load_events.js
```

Скрипт нагружает `GET /api/v1/events` (волна 10 → 20 VU). Смотрите метрики: `http_req_duration`, `http_req_failed`.

---

## Первые шаги после запуска

1. **Регистрация:** `POST /api/v1/auth/register`:
   ```json
   { "username": "user1", "email": "user1@example.com", "password": "securepass123" }
   ```

2. **Вход:** `POST /api/v1/auth/login` с `username` и `password`. В ответе — `access_token`.

3. **Запросы с авторизацией:** заголовок:
   ```
   Authorization: Bearer <access_token>
   ```

4. Если не использовали seed: чтобы сделать пользователя админом (создание событий и категорий), в БД выполните:
   ```sql
   UPDATE users SET role = 'admin' WHERE username = 'admin';
   ```
   Либо после seed используйте логин **admin** / **admin123**.

Дальше: категории — `POST /api/v1/categories`, события — `POST /api/v1/events` (от имени админа), избранное — `POST /api/v1/favorites`.
