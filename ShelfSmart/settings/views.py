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
            "id": getattr(settings, 'id', 1),
            "library_name": getattr(settings, 'library_name', 'ShelfSmart Library'),
            "theme": getattr(settings, 'theme', 'default') if getattr(settings, 'theme', 'default') in ["default", "dark", "light"] else 'default',
            "email_notifications": bool(getattr(settings, 'email_notifications', True)),
            # Backwards-compatible optional flags (may not exist on model yet)
            "due_date_reminders": bool(getattr(settings, 'due_date_reminders', False)),
            "overdue_alerts": bool(getattr(settings, 'overdue_alerts', False)),
            "items_per_page": getattr(settings, 'items_per_page', 10),
            "date_format": getattr(settings, 'date_format', 'MM/DD/YYYY'),
        }
    except Exception as e:
        print(f"Error fetching settings: {str(e)}")  # Log the error
        # Return safe defaults
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
            # store boolean
            settings.email_notifications = bool(payload["email_notifications"])
        # Optional fields (if model later includes them) - set if present in payload
        if "due_date_reminders" in payload and hasattr(settings, 'due_date_reminders'):
            setattr(settings, 'due_date_reminders', bool(payload['due_date_reminders']))
        if "overdue_alerts" in payload and hasattr(settings, 'overdue_alerts'):
            setattr(settings, 'overdue_alerts', bool(payload['overdue_alerts']))
        if "items_per_page" in payload and hasattr(settings, 'items_per_page'):
            try:
                setattr(settings, 'items_per_page', int(payload['items_per_page']))
            except (TypeError, ValueError):
                pass
        if "date_format" in payload and hasattr(settings, 'date_format'):
            setattr(settings, 'date_format', payload['date_format'])
        
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
        # Update profile fields on the logged-in user (safe, minimal validation)
        try:
            user_changed = False
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()

            if first_name and first_name != request.user.first_name:
                request.user.first_name = first_name
                user_changed = True
            if last_name and last_name != request.user.last_name:
                request.user.last_name = last_name
                user_changed = True
            if email and email != request.user.email:
                request.user.email = email
                user_changed = True

            # Try to save phone if a related profile exists
            try:
                if phone and hasattr(request.user, 'profile'):
                    if getattr(request.user.profile, 'phone', '') != phone:
                        setattr(request.user.profile, 'phone', phone)
                        request.user.profile.save()
            except Exception:
                # Ignore profile/phone save failures silently
                pass

            if user_changed:
                request.user.save()

            # Notifications and display preferences
            payload = {}
            if 'email_notifications' in request.POST:
                payload['email_notifications'] = request.POST.get('email_notifications') == 'on'
            else:
                # unchecked checkbox is absent from POST; treat as False
                payload['email_notifications'] = False

            # Additional toggles (not persisted unless AppSettings has fields)
            payload['due_date_reminders'] = request.POST.get('due_date_reminders') == 'on'
            payload['overdue_alerts'] = request.POST.get('overdue_alerts') == 'on'
            # Display preferences (accepted, may not persist if model lacks fields)
            if request.POST.get('items_per_page'):
                payload['items_per_page'] = request.POST.get('items_per_page')
            if request.POST.get('date_format'):
                payload['date_format'] = request.POST.get('date_format')

            try:
                _save_settings(payload)
            except Exception as e:
                # Log but don't crash the request; report to user
                print(f"Settings save error: {e}")
                messages.warning(request, "Some settings could not be saved to the application store.")

            messages.success(request, "Settings updated successfully")
        except Exception as e:
            print(f"Settings processing error: {e}")
            messages.error(request, "An error occurred while updating settings. Please try again.")

        return redirect("settings")

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
