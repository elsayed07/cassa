import factory

from apps.payments.models import WebhookEvent


class WebhookEventFactory(factory.django.DjangoModelFactory):
    provider = "stripe"
    provider_event_id = factory.Sequence(lambda n: f"evt_{n:010d}")
    event_type = "payment_intent.succeeded"
    payload = factory.LazyFunction(dict)
    processed = False

    class Meta:
        model = WebhookEvent
