from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any

from shared.exceptions import IllegalTransition


def transition(
    field: str,
    source: str | list[str],
    target: str,
    conditions: list[Callable[..., bool]] | None = None,
) -> Callable[..., Any]:
    """
    Decorator for model methods that perform state transitions.

    Raises IllegalTransition if the instance's current state is not in `source`.
    Optionally evaluates `conditions` (methods on self that must return True).
    Saves the model after the transition.
    """
    sources = [source] if isinstance(source, str) else source

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            current = getattr(self, field)
            if current not in sources:
                raise IllegalTransition(
                    f"Cannot transition {self.__class__.__name__}.{field} "
                    f"from '{current}' to '{target}' "
                    f"(allowed sources: {sources})"
                )
            for condition in conditions or []:
                if not condition(self):
                    raise IllegalTransition(
                        f"Transition condition '{condition.__name__}' not met on "
                        f"{self.__class__.__name__}"
                    )
            result = func(self, *args, **kwargs)
            setattr(self, field, target)
            self.save(update_fields=[field])
            return result

        wrapper._is_transition = True  # type: ignore[attr-defined]
        wrapper._source = sources  # type: ignore[attr-defined]
        wrapper._target = target  # type: ignore[attr-defined]
        wrapper._field = field  # type: ignore[attr-defined]
        return wrapper

    return decorator
