from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from dashboard.supabase_client import supabase


def _default_settings():
    return {
        "id": 1,  # singleton row id
        "library_name": "ShelfSmart Library",
        "theme": "default",
        "email_notifications": True,
        "default_borrow_days": 14,
    }


def _fetch_settings():
    try:
        # Try to get singleton settings row
        resp = supabase.table("app_settings").select("*").eq("id", 1).execute()
        if resp.data:
            # Normalize booleans that may come back as 't'/'f' or 0/1
            data = resp.data[0]
            data["email_notifications"] = bool(data.get("email_notifications", True))
            return data
    except Exception:
        # If table does not exist or any error, just fall back to defaults silently
        pass
    return _default_settings()


def _save_settings(payload: dict) -> None:
    try:
        # Upsert semantics: if id=1 exists -> update, else insert
        existing = supabase.table("app_settings").select("id").eq("id", 1).execute()
        to_save = {**_default_settings(), **payload, "id": 1}
        if existing.data:
            supabase.table("app_settings").update(to_save).eq("id", 1).execute()
        else:
            supabase.table("app_settings").insert(to_save).execute()
    except Exception:
        # Swallow errors so UI still works; caller can show a generic warning if needed
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
