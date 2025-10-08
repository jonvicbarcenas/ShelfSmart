from django.contrib import admin

from .models import PasswordResetOTP


@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "created_at", "expires_at", "is_used")
    list_filter = ("is_used", "created_at")
    search_fields = ("user__username", "user__email", "code")
    readonly_fields = ("user", "code", "created_at", "expires_at", "is_used")
