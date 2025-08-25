# 🚀 KnowYourCampus — Backend (FastAPI + PostgreSQL)

Enterprise-grade backend for **KnowYourCampus**. The service exposes a versioned REST API, persists data in PostgreSQL via SQLAlchemy, authenticates with JWT, and ships with a clean hexagonal-ish layout (routes → services → repositories → models).

---

## 🔩 Architecture at a Glance

- **Framework:** FastAPI (ASGI)
- **Runtime:** Uvicorn (dev) / Gunicorn+Uvicorn workers (prod)
- **DB:** PostgreSQL
- **ORM:** SQLAlchemy
- **Validation:** Pydantic
- **Auth:** JWT (python-jose), password hashing (passlib[bcrypt])
- **Migrations:** Alembic
- **Config:** 12-factor via environment variables

---

## 📂 Project Structure
```bash
app/
├─ api/ # HTTP edge (controllers)
│ ├─ v1/
│ │ ├─ routes_users.py # /api/v1/users
│ │ ├─ routes_auth.py # /api/v1/auth
│ │ └─ routes_algo.py # /api/v1/algo
│ └─ dependencies.py # Shared FastAPI Depends()
├─ core/ # Cross-cutting concerns
│ ├─ config.py # Settings (env vars)
│ ├─ security.py # JWT, hashing
│ ├─ logging.py # Logging setup
│ └─ exceptions.py # Global exception handlers
├─ db/
│ ├─ base.py # SQLAlchemy Base
│ ├─ session.py # Engine, SessionLocal, get_db()
│ └─ migrations/ # Alembic migration scripts
├─ models/
│ ├─ user.py
│ └─ algo_results.py
├─ repositories/ # Data access (no business logic)
│ ├─ user_repository.py
│ └─ algo_repository.py
├─ schemas/ # Pydantic I/O contracts
│ ├─ user_schemas.py
│ └─ algo_schemas.py
├─ services/ # Business logic orchestration
│ ├─ user_service.py
│ ├─ algo_service.py
│ └─ utils.py
├─ workers/ # Background jobs (Celery/RQ/FastAPI tasks)
│ └─ tasks.py
├─ tests/ # pytest suites
│ ├─ api/
│ ├─ services/
│ ├─ repositories/
│ └─ conftest.py
└─ main.py # FastAPI app bootstrap
```
---

⚙️ Setup & Installation
1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/chat-backend.git
cd chat-backend
```
2️⃣ Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows
```
3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```
4️⃣ Configure Environment Variables

Create a .env file in the root directory:
``` bash
DATABASE_URL=postgresql://username:password@localhost:5432/dbname
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
5️⃣ Start the Development Server
``` bash
uvicorn app.main:app --reload
```
---
## API Endpoints
### 🔑 Authentication

POST /auth/register → Register a new user

POST /auth/login → Login and get JWT token

### 👤 Users

GET /users/ → Get all users (requires authentication)

GET /users/{id} → Get user by ID
