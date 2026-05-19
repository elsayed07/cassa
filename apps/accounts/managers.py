from __future__ import annotations

from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager["User"]):  # type: ignore[type-arg]
    def create_user(self, email: str, password: str | None = None, **extra: object) -> "User":
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, **extra: object) -> "User":
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra)
