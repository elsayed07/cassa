from unittest.mock import MagicMock


def test_illegal_transition_raises():
    from shared.exceptions import IllegalTransition
    from apps.orders.models import Order

    order = Order.__new__(Order)
    order.status = Order.Status.COMPLETED
    order.save = MagicMock()

    import pytest
    with pytest.raises(IllegalTransition):
        order.mark_paid()


def test_valid_transition_saves():
    from apps.orders.models import Order

    order = Order.__new__(Order)
    order.status = Order.Status.AWAITING_PAYMENT
    order.save = MagicMock()

    order.mark_paid()
    assert order.status == Order.Status.PAID
    order.save.assert_called_once_with(update_fields=["status"])
