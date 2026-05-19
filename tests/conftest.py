import sys
from pathlib import Path

import pytest
from django.test import Client

# Ensure the project root is on sys.path so Django URL conf can import 'api.v1'
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests.factories.accounts import UserFactory


@pytest.fixture
def client() -> Client:
    return Client()


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def auth_client(user):
    client = Client()
    client.force_login(user)
    return client, user


@pytest.fixture
def fake_payment_provider():
    from infrastructure.payments.fake import FakePaymentProvider
    return FakePaymentProvider()
