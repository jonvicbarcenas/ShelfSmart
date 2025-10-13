from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """Allow access only to authenticated users with role == 'admin'."""
    @login_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        role = getattr(request.user, "role", "user")
        if role == "admin":
            return view_func(request, *args, **kwargs)
        messages.error(request, "You do not have permission to access this page.")
        return redirect("dashboard")
    return _wrapped
