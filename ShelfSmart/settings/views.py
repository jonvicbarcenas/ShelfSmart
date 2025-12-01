from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from .models import AppSettings


def _fetch_settings():
    """Fetch settings using Django ORM with robust error handling."""
    try:
        settings = AppSettings.get_settings()
        if not settings:
            raise ValueError("Settings not found")
            
        # Provide a simple settings dictionary with safe defaults for template rendering.
        return {
            "default_borrow_days": getattr(settings, 'default_borrow_days', 14),
            "max_renewals": getattr(settings, 'max_renewals', 2),
        }
    except Exception as e:
        print(f"Error fetching settings: {str(e)}")  # Log the error
        # Return safe defaults
        return {
            "default_borrow_days": 14,
            "max_renewals": 2,
        }


def _save_settings(payload: dict) -> None:
    """Save settings using Django ORM."""
    try:
        settings = AppSettings.get_settings()
        
        # Update fields from payload
        if "default_borrow_days" in payload:
            settings.default_borrow_days = int(payload["default_borrow_days"])
        if "max_renewals" in payload:
            settings.max_renewals = int(payload["max_renewals"])
        
        settings.save()
    except Exception:
        # Re-raise so caller can handle appropriately
        raise


def settings_home(request: HttpRequest) -> HttpResponse:
    """Settings page for managing application configuration.

    - GET: display current settings (or defaults if not configured)
    - POST: validate and save settings
    """
    if request.method == "POST":
        try:
            payload = {}
            if 'default_borrow_days' in request.POST:
                payload['default_borrow_days'] = request.POST.get('default_borrow_days')
            if 'max_renewals' in request.POST:
                payload['max_renewals'] = request.POST.get('max_renewals')

            try:
                _save_settings(payload)
                messages.success(request, "Settings updated successfully")
            except Exception as e:
                # Log but don't crash the request; report to user
                print(f"Settings save error: {e}")
                messages.warning(request, "Some settings could not be saved to the application store.")

        except Exception as e:
            print(f"Settings processing error: {e}")
            messages.error(request, "An error occurred while updating settings. Please try again.")

        return redirect("settings_app:settings")

    # GET
    context = {
        "settings": _fetch_settings(),
        "user_info": {
            "full_name": request.user.get_full_name() or "Admin User",
            "username": request.user.username,
            "role": "Admin"
        }
    }
    return render(request, "settings/settings.html", context)
