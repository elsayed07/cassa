# Cassa — Architecture

## Apps Overview

| App | Responsibility |
|---|---|
| `accounts` | Custom User (UUID PK, email-as-username), Address (billing/shipping) |
| `catalog` | Brand, Category (treebeard MP_Node), Product, ProductVariant, ProductImage |
| `inventory` | StockItem, StockMovement; reservation/commit/release services |
| `carts` | Cart (DB-backed, user OR session key), CartItem; merge on login |
| `orders` | Order (state machine), OrderItem (immutable snapshot), OrderEvent, Refund |
| `payments` | PaymentIntent, WebhookEvent; Stripe adapter behind PaymentProvider protocol |
| `coupons` | Coupon (% / fixed / free shipping), CouponRedemption (audit trail) |
| `shipping` | ShippingZone, ShippingMethod, ShippingRate; ShippingCalculator |
| `tax` | TaxZone, TaxRate (per-line, inclusive/exclusive aware); TaxCalculator |
| `wishlist` | Wishlist, WishlistItem |
| `reviews` | Review (rating + body), moderation status, aggregate cache |
| `recommendations` | Redis co-purchase sorted sets; RecommendationService |
| `notifications` | NotificationLog; transactional email service (Celery-backed) |
| `analytics` | AnalyticsEvent (append-only); admin dashboard data |
| `audit` | AuditLog; `record()` helper for staff actions |

## Order State Machine

```
                    ┌──────────────────────┐
                    │        PENDING        │
                    └──────────┬───────────┘
                               │ create_order()
                    ┌──────────▼───────────┐
                    │   AWAITING_PAYMENT    │
                    └──────────┬───────────┘
              ┌────────────────┼────────────────┐
              │ mark_paid()    │ cancel()        │ cancel()
   ┌──────────▼───────────┐   │        ┌────────▼───────┐
   │         PAID          │   │        │   CANCELLED    │
   └──────────┬───────────┘   │        └────────────────┘
              │ mark_fulfilled()
   ┌──────────▼───────────┐
   │       FULFILLED       │
   └──────────┬───────────┘
              │ mark_completed()
   ┌──────────▼───────────┐
   │       COMPLETED       │
   └──────────┬───────────┘
              │ issue_refund()
   ┌──────────▼───────────┐
   │       REFUNDED        │──► REFUND_FAILED (on provider error)
   └───────────────────────┘
```

## Checkout Flow

```
Browser                     Django                      Stripe
  │                            │                           │
  │── POST /checkout/start ───►│                           │
  │                            │─ select_for_update ──────►│ (stock)
  │                            │─ create Order (AWAITING) ─┤
  │                            │─ create_intent() ────────►│
  │                            │◄─ client_secret ──────────│
  │◄─ {client_secret} ─────────│                           │
  │                            │                           │
  │── confirmPayment() ────────────────────────────────────►│
  │                            │                           │
  │                            │◄────── webhook (payment_intent.succeeded) ──│
  │                            │─ WebhookEvent.get_or_create() ──────────────┤
  │                            │─ task.delay() in on_commit() ───────────────┤
  │                            │─ return 200 ────────────────────────────────┤
  │                            │                           │
  │                   [Celery worker]                      │
  │                            │─ Order.mark_paid()        │
  │                            │─ StockService.commit()    │
  │                            │─ send_order_confirmation()│
  │                            │─ generate_invoice_pdf()   │
  │◄─ confirmation email ──────│                           │
```

## Webhook Idempotency

Three independent safeguards prevent double-processing:

1. `WebhookEvent(provider_event_id UNIQUE)` — database-level dedup. `get_or_create` on event ID; if row already exists, return 200 immediately.
2. **State machine** — `Order.mark_paid()` raises `IllegalTransition` if `order.status != AWAITING_PAYMENT`. A second `payment_intent.succeeded` event for the same order is a no-op.
3. `StockMovement(reservation_uuid)` — each reservation is tagged with a UUID. `commit()` with the same UUID is idempotent.

## Recommendation Engine

Uses Redis sorted sets (no ML required):

```
Key: recommendations:{product_id}
Members: co-purchased product IDs
Scores: co-occurrence count
```

The `update_recommendation_scores` Celery beat task (daily 02:00) reads `OrderItem` pairs from the last 90 days and rebuilds the sorted sets. `GET /api/v1/catalog/products/{id}/recommendations/` returns `ZREVRANGE recommendations:{id} 0 9`.

## Service / Selector Pattern

```
View / API endpoint
    │
    ├── Selector  (reads: complex queries, aggregations)
    │       └── Returns typed dicts or model instances
    │
    └── Service   (writes: all state changes)
            ├── Validates inputs (raises ApplicationError subclass)
            ├── Runs inside transaction.atomic()
            └── Wraps side-effect tasks in transaction.on_commit()
```

Views contain no business logic. Services accept domain objects, never `request`.

## Key Design Decisions

- **`BaseModel`** (UUID PK + `created_at`, `updated_at` + soft delete) on all domain models. UUID prevents order-count enumeration via URLs.
- **`Money` value object** centralises rounding and currency-mixing guards. One place to update when adding a new zero-decimal currency.
- **`OrderItem` is a snapshot**, not a FK to live product data. Repricing a product never rewrites historical order lines.
- **Single `config/settings.py`** driven by `DJANGO_ENV`. No base/dev/prod split — pydantic-settings catches misconfiguration at startup.
- **Tailwind compiled** — JIT-compiled bundle (~30 KB), not the CDN build (~3 MB).
- **`transaction.on_commit()`** wrapping all Celery `.delay()` calls — tasks only fire after the triggering transaction commits.
