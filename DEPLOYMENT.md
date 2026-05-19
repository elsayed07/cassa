# Cassa — Deployment

## Prerequisites

- Docker and Docker Compose v2
- A PostgreSQL 17 instance (or use the bundled container)
- A Redis 7 instance
- An S3-compatible bucket (AWS S3 or MinIO)
- A Stripe account with a webhook endpoint configured
- An SMTP provider (Postmark, SES, or Mailgun via django-anymail)

## Environment Variables

Copy `.env.example` to `.env` and fill in all values.

```bash
# Django
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(50))">
DJANGO_ENV=production
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=cassa
DB_USER=cassa
DB_PASSWORD=<strong password>

# Redis
REDIS_URL=redis://redis:6379/0

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Storage (S3)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=cassa-media
AWS_S3_ENDPOINT_URL=          # leave blank for AWS, set for MinIO
AWS_S3_CUSTOM_DOMAIN=         # CDN domain, optional

# Email (anymail)
EMAIL_BACKEND=anymail.backends.postmark.EmailBackend
ANYMAIL_POSTMARK_SERVER_TOKEN=...
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Store
CASSA_STORE_NAME=Cassa
CASSA_STORE_URL=https://yourdomain.com
CASSA_CURRENCY=USD

# Sentry (optional)
SENTRY_DSN=https://...@sentry.io/...

# Google OAuth (optional)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

## First Deployment

```bash
# 1. Build images
docker compose -f docker-compose.prod.yml build

# 2. Start all services
docker compose -f docker-compose.prod.yml up -d

# 3. Run migrations
docker compose -f docker-compose.prod.yml exec django python manage.py migrate

# 4. Collect static files
docker compose -f docker-compose.prod.yml exec django python manage.py collectstatic --noinput

# 5. Create superuser
docker compose -f docker-compose.prod.yml exec django python manage.py createsuperuser

# 6. Create the django-celery-beat initial schedule
docker compose -f docker-compose.prod.yml exec django python manage.py migrate django_celery_beat
```

## Stripe Webhook Setup

1. In the Stripe Dashboard → Webhooks → Add endpoint:
   - URL: `https://yourdomain.com/webhooks/stripe/`
   - Events: `payment_intent.succeeded`, `payment_intent.payment_failed`, `checkout.session.expired`, `charge.refunded`

2. Copy the signing secret to `STRIPE_WEBHOOK_SECRET` in `.env`.

3. Test the webhook:
   ```bash
   stripe trigger payment_intent.succeeded
   ```

## Scaling

- **Django**: Increase `--workers` on the gunicorn command (CPU-bound work: 2× CPU cores).
- **Celery**: Increase `--concurrency` or add more `celery` replicas. Use separate queues for `email`, `pdf`, `recommendations` if throughput warrants.
- **Database**: Add `pgBouncer` in front of PostgreSQL for connection pooling at scale.

## Runbook

### Stuck Celery Task

```bash
docker compose -f docker-compose.prod.yml exec django python manage.py shell
>>> from celery import current_app
>>> current_app.control.inspect().active()
>>> current_app.control.revoke('<task-id>', terminate=True)
```

### Release Stuck Stock Reservation

```bash
python manage.py shell
>>> from apps.inventory.services.stock import StockService
>>> StockService.release_expired(older_than_minutes=60)
```

### Trigger Abandoned Cart Sweep Manually

```bash
docker compose -f docker-compose.prod.yml exec celery python -m celery -A infrastructure.celery call apps.carts.tasks.sweep_abandoned_carts
```

### Check Order Payment State

```bash
python manage.py shell
>>> from apps.orders.models import Order
>>> o = Order.objects.get(number='ORD-XXXX')
>>> print(o.status, o.payment_intents.last().provider_status)
```
