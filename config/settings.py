from __future__ import annotations

from pathlib import Path

from config.env import BASE_DIR, db, email, redis, sentry, settings, storage, stripe

SECRET_KEY = settings.secret_key
DEBUG = settings.debug
ALLOWED_HOSTS = settings.allowed_hosts

INSTALLED_APPS = [
    # Unfold must come before django.contrib.admin
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    # Third-party
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "ninja",
    "celery",
    "django_celery_beat",
    "django_celery_results",
    "django_htmx",
    "django_prometheus",
    "parler",
    "treebeard",
    "tailwind",
    # Local
    "apps.accounts",
    "apps.catalog",
    "apps.inventory",
    "apps.carts",
    "apps.orders",
    "apps.payments",
    "apps.coupons",
    "apps.shipping",
    "apps.tax",
    "apps.wishlist",
    "apps.reviews",
    "apps.recommendations",
    "apps.notifications",
    "apps.analytics",
    "apps.audit",
    # Tailwind theme app (created by django-tailwind)
    "theme",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "infrastructure.logging.RequestIdMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "apps.carts.context_processors.cart",
            ],
        },
    },
]

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": db.name,
        "USER": db.user,
        "PASSWORD": db.password,
        "HOST": db.host,
        "PORT": db.port,
        "CONN_MAX_AGE": 60,
        "CONN_HEALTH_CHECKS": True,
        "OPTIONS": {"connect_timeout": 10},
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Cache
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": redis.url,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
        },
    }
}

# Session
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30 days
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# Auth
AUTH_USER_MODEL = "accounts.User"
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Allauth
SITE_ID = 1
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "APP": {
            "client_id": settings.google_client_id,
            "secret": settings.google_client_secret,
        },
    }
}

# Internationalization
LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", "English"),
    ("es", "Español"),
    ("fr", "Français"),
    ("de", "Deutsch"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Tailwind
TAILWIND_APP_NAME = "theme"
INTERNAL_IPS = ["127.0.0.1"]

# Celery
CELERY_BROKER_URL = redis.url.replace("/0", "/1")
CELERY_RESULT_BACKEND = "django-db"
CELERY_RESULT_EXTENDED = True
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 300
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# Email
EMAIL_BACKEND = email.backend
EMAIL_HOST = email.host
EMAIL_PORT = email.port
EMAIL_USE_TLS = email.use_tls
EMAIL_HOST_USER = email.host_user
EMAIL_HOST_PASSWORD = email.host_password
DEFAULT_FROM_EMAIL = email.default_from

# Stripe
STRIPE_SECRET_KEY = stripe.secret_key
STRIPE_PUBLISHABLE_KEY = stripe.publishable_key
STRIPE_WEBHOOK_SECRET = stripe.webhook_secret

# Storage — prod uses S3/MinIO; dev uses local filesystem
if settings.django_env == "production":
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_ACCESS_KEY_ID = storage.access_key_id
    AWS_SECRET_ACCESS_KEY = storage.secret_access_key
    AWS_STORAGE_BUCKET_NAME = storage.storage_bucket_name
    AWS_S3_ENDPOINT_URL = storage.s3_endpoint_url or None
    AWS_S3_CUSTOM_DOMAIN = storage.s3_custom_domain or None
    AWS_DEFAULT_ACL = None
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = False

# Django Ninja JWT settings
NINJA_JWT = {
    "ACCESS_TOKEN_LIFETIME_MINUTES": 60,
    "REFRESH_TOKEN_LIFETIME_DAYS": 7,
}

# Parler
PARLER_LANGUAGES = {
    None: (
        {"code": "en"},
        {"code": "es"},
        {"code": "fr"},
        {"code": "de"},
    ),
    "default": {"fallbacks": ["en"], "hide_untranslated": False},
}

# Security (tightened in production)
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True

if settings.django_env == "production":
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Debug toolbar (dev only)
if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")

# Testing overrides
if settings.django_env == "testing":
    CELERY_TASK_ALWAYS_EAGER = True
    PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
    EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    ACCOUNT_EMAIL_VERIFICATION = "none"

# Sentry
if sentry.dsn:
    import sentry_sdk

    sentry_sdk.init(
        dsn=sentry.dsn,
        environment=sentry.environment,
        traces_sample_rate=sentry.traces_sample_rate,
        integrations=[],
    )

# Ecommerce
CASSA_CURRENCY = settings.currency
CASSA_STORE_NAME = settings.store_name
CASSA_STORE_URL = settings.store_url
CASSA_ABANDONED_CART_HOURS = 4
CASSA_INVOICE_PDF_STORAGE = "invoices/"
CASSA_LOW_STOCK_THRESHOLD = 5
