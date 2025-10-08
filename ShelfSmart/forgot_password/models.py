from __future__ import annotations

import secrets
import string

from django.conf import settings
from django.db import models
from django.utils import timezone


OTP_CODE_LENGTH = 6
OTP_EXPIRATION_MINUTES = 10


def _generate_otp_code(length: int = OTP_CODE_LENGTH) -> str:
    digits = string.digits
    return "".join(secrets.choice(digits) for _ in range(length))


class PasswordResetOTPManager(models.Manager):
    def create_for_user(self, user: settings.AUTH_USER_MODEL) -> "PasswordResetOTP":
        self.filter(user=user, is_used=False).update(is_used=True)

        code = _generate_otp_code()
        expires_at = timezone.now() + timezone.timedelta(minutes=OTP_EXPIRATION_MINUTES)

        return super().create(user=user, code=code, expires_at=expires_at)

    def validate_otp(self, user: settings.AUTH_USER_MODEL, code: str) -> "PasswordResetOTP":
        otp = (
            self.filter(user=user, code=code, is_used=False)
            .order_by("-created_at")
            .first()
        )

        if otp is None:
            raise self.model.DoesNotExist("Invalid OTP code")

        if otp.is_expired:
            raise self.model.Expired("OTP code has expired")

        return otp


class PasswordResetOTP(models.Model):
    class Expired(Exception):
        """Raised when an OTP has expired."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="password_reset_otps")
    code = models.CharField(max_length=OTP_CODE_LENGTH)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    objects = PasswordResetOTPManager()

    class Meta:
        indexes = [
            models.Index(fields=["user", "code", "is_used"]),
            models.Index(fields=["expires_at"]),
        ]
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"PasswordResetOTP(user={self.user_id}, code={self.code})"

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    def mark_as_used(self) -> None:
        if not self.is_used:
            self.is_used = True
            self.save(update_fields=["is_used"])
