from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from .models import AppSettings


def _fetch_settings():
    """Fetch settings using Django ORM."""
    try:
        settings = AppSettings.get_settings()
        return {
            "id": settings.id,
            "library_name": settings.library_name,
            "theme": settings.theme,
            "email_notifications": settings.email_notifications,
            "default_borrow_days": settings.default_borrow_days,
        }
    except Exception:
        # Fallback to defaults if any error
        return {
            "id": 1,
            "library_name": "ShelfSmart Library",
            "theme": "default",
            "email_notifications": True,
            "default_borrow_days": 14,
        }


def _save_settings(payload: dict) -> None:
    """Save settings using Django ORM."""
    try:
        settings = AppSettings.get_settings()
        
        # Update fields from payload
        if "library_name" in payload:
            settings.library_name = payload["library_name"]
        if "theme" in payload:
            settings.theme = payload["theme"]
        if "email_notifications" in payload:
            settings.email_notifications = bool(payload["email_notifications"])
        if "default_borrow_days" in payload:
            settings.default_borrow_days = int(payload["default_borrow_days"])
        
        settings.save()
    except Exception:
        # Re-raise so caller can handle appropriately
        raise


def settings_home(request: HttpRequest) -> HttpResponse:
    """Settings page with Supabase integration.

    - GET: display current settings (or defaults if table missing)
    - POST: save settings to Supabase `app_settings` table (singleton row id=1)
    """
    if request.method == "POST":
        library_name = request.POST.get("library_name", "ShelfSmart Library").strip()
        theme = request.POST.get("theme", "default").strip()
        email_notifications = request.POST.get("email_notifications") == "on"
        try:
            default_borrow_days = int(request.POST.get("default_borrow_days", 14))
        except (TypeError, ValueError):
            default_borrow_days = 14

        payload = {
            "library_name": library_name or "ShelfSmart Library",
            "theme": theme or "default",
            "email_notifications": email_notifications,
            "default_borrow_days": max(1, min(default_borrow_days, 60)),
        }
        try:
            _save_settings(payload)
            messages.success(request, "Settings have been saved successfully.")
        except Exception as e:
            messages.error(request, f"Unable to save settings right now. {e}")
        return redirect("settings")

    # GET
    context = {"settings": _fetch_settings()}
    return render(request, "settings/settings.html", context)
