from __future__ import annotations

from typing import Any

from ninja import Router, Schema

router = Router()


class ProfileOut(Schema):
    email: str
    first_name: str
    last_name: str


@router.get("/me/", response=ProfileOut)
def me(request: Any) -> Any:
    return request.auth
