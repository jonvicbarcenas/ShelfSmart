"""
Decorators for role-based access control.
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def admin_required(view_func):
    """
    Decorator to restrict access to admin users only.
    Regular users will be redirected to their dashboard with an error message.
    """
    @wraps(view_func)
    @login_required(login_url='/login/')
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.user_type == 'admin':
            messages.error(request, "You don't have permission to access this page.")
            return redirect('/user/dashboard/')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def user_required(view_func):
    """
    Decorator to restrict access to regular users only.
    Admin users will be redirected to their dashboard.
    """
    @wraps(view_func)
    @login_required(login_url='/login/')
    def _wrapped_view(request, *args, **kwargs):
        if request.user.user_type == 'admin':
            return redirect('/admin-panel/dashboard/')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
