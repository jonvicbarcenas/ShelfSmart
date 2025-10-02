from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods


def _is_ajax(request) -> bool:
    """Return True when the request originates from an XMLHttpRequest."""

    return request.headers.get("x-requested-with") == "XMLHttpRequest"


@login_required
@require_http_methods(["GET", "POST"])
def logout_view(request):
    """Log out the current user and redirect to the login page."""

    redirect_url = reverse("user_auth:login")

    logout(request)

    if _is_ajax(request):
        return JsonResponse({"success": True, "redirect_url": redirect_url})

    messages.info(request, "You have been signed out.")
    return redirect(redirect_url)
