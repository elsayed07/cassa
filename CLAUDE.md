# CLAUDE.md — Cassa Ecommerce Conventions

Ecommerce-specific rules. These are the invariants the codebase is built around.
Violating them causes subtle money bugs that are hard to find post-deployment.

## Money

- **Always use `Money`** (from `shared.money`) for prices, totals, discounts, and refunds. Never use bare `Decimal` or `float` for currency values.
- `Money.__add__` raises `ValueError` on currency mismatch. This is intentional.
- Store monetary amounts in the DB as `DecimalField(max_digits=12, decimal_places=2)` + a `currency` `CharField`. Never store cents as integers in the DB (Stripe uses cents; we convert at the boundary with `Money.as_cents()` / `Money.from_cents()`).
- JPY and a handful of other currencies are zero-decimal (no fractional units). The `ZERO_DECIMAL_CURRENCIES` set in `shared/money.py` governs this. `as_cents()` returns the face value unchanged for these.

## OrderItem is immutable

- `OrderItem` fields (`product_name`, `sku`, `unit_price`, `line_total`) are snapshotted at order creation and **never updated**.
- An order is a financial record. Product renames, price changes, or deletions must not silently rewrite historical line items.
- Do not add `ForeignKey` to live `Product` or `ProductVariant` from `OrderItem` for price/name retrieval — read the snapshot fields.

## State machine

- Use `@transition(field=..., source=..., target=...)` from `shared.state_machine` to drive `Order.status` changes.
- Calling a transition method when the model is in a disallowed source state raises `IllegalTransition`. Catch this at the service layer, never in the view.
- Never set `order.status = Order.Status.PAID` directly. Always call the transition method (`order.mark_paid()`).
- The transition decorator calls `self.save(update_fields=[field])` after the method body. Do not call `save()` yourself inside transition methods.

## Coupons

- **Never hard-delete a Coupon row.** Use soft delete (`deleted_at`). Historical `CouponRedemption` records reference the coupon; hard deletion breaks audit trails.
- Validation order: active check → date range → min_subtotal → max_uses → max_uses_per_user. Stop at the first failure and raise `CouponError` with a user-facing message.
- `CouponRedemption` has a `(coupon, order)` unique constraint. Use `get_or_create` when recording redemptions to be idempotent.

## Celery + transactions

- **Always wrap `.delay()` calls in `transaction.on_commit()`**:
  ```python
  transaction.on_commit(lambda: my_task.delay(obj.pk))
  ```
  Tasks that fire before the DB row is visible to other connections cause "not found" errors. This is especially critical in `CheckoutService` where the order row must be committed before the confirmation-email task runs.

## Stock reservations

- `StockService.reserve()` and `StockService.commit()` use `select_for_update()`. They must be called inside `transaction.atomic()`.
- Each reservation carries a `reservation_uuid`. The same UUID is passed through to `commit()` and `release()`. This makes double-commits detectable.
- On payment failure or session expiry, always call `StockService.release()`. The `release_expired_stock_reservations` beat task is the safety net, not the primary mechanism.

## Webhook idempotency

- `WebhookEvent(provider_event_id UNIQUE)` is the idempotency key. Use `get_or_create(provider_event_id=event.id)`. If not `created`, return `200` immediately — Stripe has already been acknowledged.
- Never process webhook events synchronously in the view. Enqueue a Celery task inside `transaction.on_commit()` and return `200` immediately.
- The Celery task for webhook processing must be idempotent itself (retry-safe). Check `WebhookEvent.status` at the start of the task.

## Service / Selector pattern

- All writes (checkout, stock mutation, coupon redemption, refund issuance) go through **service classes** in `apps/<app>/services/`.
- All complex reads (cart total computation, product search, order history) go through **selector classes** in `apps/<app>/selectors.py`.
- Views call services and selectors; they contain no business logic themselves.
- Services are pure Python — no request/response coupling. They accept domain objects, not `request`.

## Soft delete

- Domain models inherit `BaseModel` which includes `SoftDeleteModel`. `obj.delete()` sets `deleted_at`, not removes the row.
- The default manager (`objects`) filters out soft-deleted rows. `all_objects` includes them.
- Never call `queryset.delete()` on domain tables without understanding what FK-dependent rows will be orphaned.

## Translation (parler)

- `Product`, `Category`, and `Brand` use `django-parler` for translated fields (`name`, `description`, `slug`).
- Always use `product.safe_translation_getter("name", language_code=request.LANGUAGE_CODE)` when rendering product names, not bare `product.name`, to avoid `TranslationDoesNotExist` exceptions.
- Parler translations live in sibling `*Translation` tables. Migrations for translation models are auto-generated by parler.
