from __future__ import annotations

from http import HTTPStatus


class ApplicationError(Exception):
    """Base for all domain errors. HTTP status is advisory for API layer."""

    http_status: int = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__


class NotFoundError(ApplicationError):
    http_status = HTTPStatus.NOT_FOUND


class ConflictError(ApplicationError):
    http_status = HTTPStatus.CONFLICT


class ValidationError(ApplicationError):
    http_status = HTTPStatus.UNPROCESSABLE_ENTITY


class AuthorizationError(ApplicationError):
    http_status = HTTPStatus.FORBIDDEN


class AuthenticationError(ApplicationError):
    http_status = HTTPStatus.UNAUTHORIZED


class PaymentError(ApplicationError):
    http_status = HTTPStatus.PAYMENT_REQUIRED


class StockError(ConflictError):
    """Raised when stock is insufficient or reservation fails."""


class IllegalTransition(ConflictError):
    """Raised when a state-machine transition is not allowed."""


class CouponError(ValidationError):
    """Raised when a coupon cannot be applied."""


class CartError(ValidationError):
    """Raised for invalid cart operations."""
