# Cassa

Production-grade ecommerce platform built with Django 5.2.

## Stack

- **Backend**: Python 3.13, Django 5.2, PostgreSQL 17
- **Queue**: Celery 5 + Redis 7
- **API**: Django Ninja + JWT auth
- **Auth**: django-allauth (email, Google OAuth)
- **Payments**: Stripe (Checkout Session / Payment Elements)
- **Frontend**: HTMX + Alpine.js + compiled Tailwind CSS
- **Storage**: MinIO (dev) / S3 (prod)
- **Email**: Mailpit (dev) / Postmark or SES (prod)

## Quickstart

**Prerequisites**: Docker Desktop, Python 3.13, Node 18+, uv

```bash
# 1. Clone and enter
cd G:/Projects/cassa

# 2. Install Python dependencies
pip install uv
uv sync

# 3. Copy and edit environment
cp .env.example .env
# Edit .env — at minimum set SECRET_KEY and STRIPE_* keys

# 4. Start services
make up

# 5. Run migrations and seed
make migrate
make seed

# 6. (Optional) Install Stripe CLI for webhook forwarding
stripe listen --forward-to localhost:8000/webhooks/stripe/

# 7. Start dev server
make dev
```

Open http://localhost:8000 — admin at http://localhost:8000/admin/

**Dev credentials** (after `make seed`):
- Admin: `admin@cassa.dev` / `adminpass123`
- Staff: `staff@cassa.dev` / `staffpass123`
- Customer: `customer@cassa.dev` / `customerpass123`

**Dev tooling**:
- Mailpit: http://localhost:8025
- MinIO: http://localhost:9001 (minioadmin / minioadmin)
- API docs: http://localhost:8000/api/v1/docs

## Development

```bash
make dev          # runserver + tailwind watch
make test         # pytest with coverage
make lint         # ruff check + format
make typecheck    # pyright
make migrate      # makemigrations + migrate
make seed         # populate dev data
make messages     # extract + compile i18n strings
make shell        # Django shell_plus
make logs         # docker compose logs -f
```

## Stripe Testing

Use Stripe test cards at checkout:
- `4242 4242 4242 4242` — succeeds
- `4000 0000 0000 9995` — declines (insufficient funds)
- `4000 0025 0000 3155` — 3DS required

Forward webhooks locally:
```bash
stripe listen --forward-to localhost:8000/webhooks/stripe/
```

## Environment Variables

See `.env.example` for the full list. Critical variables:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key (generate with `python -c "import secrets; print(secrets.token_urlsafe(50))"`) |
| `DJANGO_ENV` | `development` / `production` / `testing` |
| `DB_*` | PostgreSQL connection (host, port, name, user, password) |
| `REDIS_URL` | Redis connection URL |
| `STRIPE_SECRET_KEY` | Stripe secret key (`sk_test_...`) |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key (`pk_test_...`) |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret (`whsec_...`) |

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for a detailed overview including the ERD, checkout flow, and state machine diagram.

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup, S3 configuration, and runbooks.
