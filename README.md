# Cassa

Production-grade Django 5 ecommerce platform.

## Features

- **Product catalog** — hierarchical categories, product variants, full-text search, translations (django-parler)
- **Shopping cart** — session-based and persistent carts, automatic merge on login
- **Checkout** — multi-step flow, coupon codes, tax calculation, shipping zones
- **Payments** — Stripe Checkout Session + webhook processing with full idempotency
- **Inventory** — per-SKU stock tracking, atomic reserve/commit/release with double-commit protection
- **Orders** — state machine (PENDING → AWAITING_PAYMENT → PAID → FULFILLED → SHIPPED → DELIVERED), partial/full refunds
- **Coupons** — percentage, fixed-amount, and free-shipping types; min_subtotal, global usage limits, per-user limits; soft-delete for audit integrity
- **Recommendations** — collaborative filtering ("customers also bought")
- **Wishlists** — per-user wishlist with move-to-cart
- **Reviews** — verified-purchase reviews with moderation queue
- **Analytics** — pageview tracking, abandoned cart recovery
- **Accounts** — email + Google OAuth (django-allauth), address book, order history
- **REST API** — Django Ninja + JWT auth, OpenAPI docs at `/api/v1/docs`
- **i18n** — URL-based language switching, translated product names/descriptions/slugs
- **Async tasks** — Celery + Redis (transactional emails, webhook dispatch, stock cleanup)
- **Audit log** — append-only write history for orders, payments, and inventory

## Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| Framework | Django 5.2 |
| Database | PostgreSQL 17 |
| Cache / Broker | Redis 7 |
| Task queue | Celery 5 |
| REST API | Django Ninja + JWT |
| Auth | django-allauth (email + Google OAuth) |
| Payments | Stripe |
| Frontend | HTMX + Alpine.js + Tailwind CSS |
| Object storage | MinIO (dev) / AWS S3 (prod) |
| Email | Mailpit (dev) / Postmark or SES (prod) |
| PDF generation | WeasyPrint (invoices) |

## Quick Start

**Prerequisites**: Docker Desktop, Python 3.13, [`uv`](https://docs.astral.sh/uv/)

```bash
git clone https://github.com/elsayedghoonaim/cassa.git
cd cassa

# Install Python dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env — at minimum set SECRET_KEY, DB_*, REDIS_URL, and STRIPE_* keys

# Start backing services (PostgreSQL, Redis, MinIO, Mailpit)
make up

# Run migrations and seed dev data
make migrate
make seed

# Start dev server + Tailwind watcher
make dev
```

Open [http://localhost:8000](http://localhost:8000) — admin at [http://localhost:8000/admin/](http://localhost:8000/admin/)

Dev credentials (created by `make seed`):

| Role | Email | Password |
|---|---|---|
| Admin | admin@cassa.dev | adminpass123 |
| Staff | staff@cassa.dev | staffpass123 |
| Customer | customer@cassa.dev | customerpass123 |

Dev services:

| Service | URL |
|---|---|
| API docs (OpenAPI) | http://localhost:8000/api/v1/docs |
| Mailpit (email) | http://localhost:8025 |
| MinIO console | http://localhost:9001 |

## Development

```bash
make dev          # runserver + Tailwind watch
make test         # pytest with coverage report
make lint         # ruff check + format
make typecheck    # pyright
make migrate      # makemigrations + migrate
make seed         # populate dev data
make messages     # extract + compile i18n strings
make shell        # Django shell_plus
make logs         # docker compose logs -f
```

## Testing

51 tests across unit, integration, and API layers:

```
tests/
├── unit/
│   ├── test_money.py             # Money value object (arithmetic, currency mismatch)
│   ├── test_state_machine.py     # Order state transitions + IllegalTransition guards
│   └── test_coupon_service.py    # Validation order, discount calculation, edge cases
├── integration/
│   ├── test_stock_service.py     # reserve / commit / release, double-commit protection
│   ├── test_webhook.py           # Stripe idempotency, retry safety, signature verification
│   └── test_shipping.py          # Zone matching, flat/free rates, unknown country fallback
└── api/
    └── test_catalog.py           # Product list, detail, search, categories (REST)
```

Run tests:

```bash
make test
# or directly:
uv run pytest --tb=short -q
```

## Stripe

Forward webhooks locally with the [Stripe CLI](https://stripe.com/docs/stripe-cli):

```bash
stripe listen --forward-to localhost:8000/webhooks/stripe/
```

Test cards:

| Card number | Outcome |
|---|---|
| `4242 4242 4242 4242` | Success |
| `4000 0000 0000 9995` | Decline — insufficient funds |
| `4000 0025 0000 3155` | 3D Secure required |

## Environment Variables

See [`.env.example`](.env.example) for the full list. Critical variables:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key (`python -c "import secrets; print(secrets.token_urlsafe(50))"`) |
| `DJANGO_ENV` | `development` / `production` / `testing` |
| `DB_HOST` / `DB_PORT` / `DB_NAME` / `DB_USER` / `DB_PASSWORD` | PostgreSQL connection |
| `REDIS_URL` | Redis connection URL |
| `STRIPE_SECRET_KEY` | Stripe secret key (`sk_test_...`) |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key (`pk_test_...`) |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret (`whsec_...`) |

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for a detailed overview including the ERD, checkout flow, and order state machine diagram.

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup (Docker Compose, Nginx, S3, environment hardening) and operational runbooks.

## License

MIT
