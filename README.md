# Dental Clinic API

A FastAPI backend with SQLite-backed user registration. New users are saved to
the database, and passwords are stored as secure hashes rather than plaintext.

## Requirements

- Python 3.14 or newer
- [uv](https://docs.astral.sh/uv/)

## Setup

From the project root, install the dependencies and create your local
environment file:

```powershell
uv sync
Copy-Item .env.example .env
```

Edit `.env` to configure the app. For example:

```dotenv
DATABASE_URL=sqlite:///./dental_clinic.db
```

The SQLite URL above is the default. Keep passwords, signing keys, tokens, and
other private values only in `.env` or your deployment's secret manager. Real
`.env` files are ignored by Git; `.env.example` contains configuration
placeholders only and is safe to commit. Do not put real secrets in source code,
documentation, or `.env.example`.

## Run

Start the API from the project root:

```powershell
uv run dental-clinic
```

The service listens on `http://127.0.0.1:8000`. Interactive API documentation
is available at `http://127.0.0.1:8000/docs`.

## API

### Health check

`GET /health` returns:

```json
{
  "status": "ok"
}
```

### Register a user

Send `POST /auth/signup` with a JSON body:

```json
{
  "full_name": "Alex Patient",
  "email": "alex@example.com",
  "password": "a-long-password"
}
```

A successful registration returns `201 Created`. The response includes the
user's ID, name, email, role, and active status; it never returns the password
or password hash. Email addresses are normalized to lowercase. Reusing an email
returns `409 Conflict`.

The database tables are created when the API starts. With the default
configuration, the database is `dental_clinic.db` in the project directory.

## Tests

Run the test suite with:

```powershell
uv run pytest
```
