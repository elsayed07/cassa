from __future__ import annotations

import json
from unittest.mock import patch

import pytest


@pytest.mark.django_db
class TestWebhookIdempotency:
    def _post_event(self, client, event_id: str, event_type: str = "payment_intent.succeeded"):
        payload = json.dumps({"id": event_id, "type": event_type})
        with patch(
            "apps.payments.views.StripeProvider.verify_webhook",
            return_value={"id": event_id, "type": event_type},
        ):
            return client.post(
                "/webhooks/stripe/",
                data=payload,
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="test",
            )

    def test_first_event_creates_webhook_record(self, client) -> None:
        from apps.payments.models import WebhookEvent

        self._post_event(client, "evt_first_001")
        assert WebhookEvent.objects.filter(provider_event_id="evt_first_001").exists()

    def test_duplicate_event_returns_200_without_duplicate_record(self, client) -> None:
        from apps.payments.models import WebhookEvent

        self._post_event(client, "evt_dup_001")
        response = self._post_event(client, "evt_dup_001")

        assert response.status_code == 200
        assert WebhookEvent.objects.filter(provider_event_id="evt_dup_001").count() == 1

    def test_invalid_signature_returns_400(self, client) -> None:
        from shared.exceptions import PaymentError

        with patch(
            "apps.payments.views.StripeProvider.verify_webhook",
            side_effect=PaymentError("bad sig"),
        ):
            response = client.post(
                "/webhooks/stripe/",
                data="{}",
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="bad",
            )
        assert response.status_code == 400


@pytest.mark.django_db
class TestProcessEventIdempotency:
    def test_already_processed_event_is_skipped(self) -> None:
        from unittest.mock import patch
        from apps.payments.views import _process_event
        from tests.factories.payments import WebhookEventFactory

        event = WebhookEventFactory(processed=True)

        with patch("apps.payments.views._dispatch_event") as mock_dispatch:
            _process_event.run(str(event.id))
            mock_dispatch.assert_not_called()

    def test_unprocessed_event_is_dispatched(self) -> None:
        from unittest.mock import patch
        from apps.payments.views import _process_event
        from tests.factories.payments import WebhookEventFactory

        event = WebhookEventFactory(processed=False)

        with patch("apps.payments.views._dispatch_event") as mock_dispatch:
            _process_event.run(str(event.id))
            mock_dispatch.assert_called_once()

        event.refresh_from_db()
        assert event.processed is True
