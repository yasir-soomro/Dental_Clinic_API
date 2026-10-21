# Dental Clinic API

A FastAPI service that stores user accounts in a SQLAlchemy database and
provides signup and login endpoints. Passwords are hashed before storage.

## Requirements

- Python 3.14 or newer
- [uv](https://docs.astral.sh/uv/)

## Setup

Run these commands in the project root:

```powershell
uv sync
Copy-Item .env.example .env
```

Generate a private signing key:

```powershell
uv run python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Set the generated value as `SECRET_KEY` in `.env`. The remaining settings can
also be adjusted there:

```dotenv
DATABASE_URL=sqlite:///./dental_clinic.db
SECRET_KEY=replace-this-with-your-generated-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

The application requires `SECRET_KEY` to be set. Keep real secrets in `.env` or
your deployment's secret manager. Git ignores `.env` files; `.env.example`
contains placeholders and is safe to commit. Never put real keys, passwords,
or tokens in source code or documentation.

## Run the API

```powershell
uv run dental-clinic
```

The API listens at `http://127.0.0.1:8000`. Open
`http://127.0.0.1:8000/docs` for interactive Swagger documentation.

The database tables are created at startup. With the default configuration,
SQLite data is stored in `dental_clinic.db` in the project root. Set
`DATABASE_URL` in `.env` to use a different SQLAlchemy database URL.

## Endpoints

### `GET /health`

Returns `200 OK` when the service is available:

```json
{
  "status": "ok"
}
```

### `POST /auth/signup`

Creates an account and returns `201 Created`. Email addresses are normalized
to lowercase. Duplicate addresses return `409 Conflict`; invalid input returns
`422 Unprocessable Entity`.

Request:

```json
{
  "full_name": "Alex Patient",
  "email": "alex@example.com",
  "password": "a-long-password"
}
```

The response contains the user's ID, name, email, role, and active status. It
does not include the password or password hash.

### `POST /auth/login`

Checks the email and password and returns a signed access token:

```json
{
  "email": "alex@example.com",
  "password": "a-long-password"
}
```

Successful response:

```json
{
  "access_token": "<signed-token>",
  "token_type": "bearer"
}
```

Invalid credentials return `401 Unauthorized`. Inactive accounts return
`403 Forbidden`. Token expiry is controlled by
`ACCESS_TOKEN_EXPIRE_MINUTES`.

## Project structure

```text
src/dental_clinic/
├── core/       Application settings and security helpers
├── db/         SQLAlchemy base, engine, and session dependency
├── models/     Database models
├── routers/    FastAPI endpoint modules
├── schemas/    Request and response validation models
├── services/   Authentication and account business logic
├── cli.py      Command-line entry point
└── main.py     FastAPI application factory and startup
tests/
├── conftest.py    Shared isolated database and API client fixture
├── test_auth.py   Signup, login, and validation tests
├── test_cli.py    CLI startup test
└── test_health.py Health endpoint test
```

## Run tests

```powershell
uv run pytest
```
