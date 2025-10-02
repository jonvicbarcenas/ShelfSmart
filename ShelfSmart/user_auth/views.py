from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import LoginForm, SignupForm


def _is_ajax(request) -> bool:
    """Return True when the request originates from an XMLHttpRequest."""

    return request.headers.get("x-requested-with") == "XMLHttpRequest"


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = LoginForm(request=request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            redirect_url = (
                request.POST.get("next")
                or request.GET.get("next")
                or reverse("dashboard")
            )
            auth_login(request, form.get_user())
            if _is_ajax(request):
                return JsonResponse({"success": True, "redirect_url": redirect_url})
            return redirect(redirect_url)

        non_field_errors = form.non_field_errors()
        error_message = (
            non_field_errors[0]
            if non_field_errors
            else "Please correct the errors below."
        )
        if _is_ajax(request):
            return JsonResponse(
                {
                    "success": False,
                    "error": error_message,
                    "field_errors": form.errors.get_json_data(),
                },
                status=400,
            )
        messages.error(request, error_message)

    context = {
        "form": form,
        "next": request.POST.get("next") or request.GET.get("next") or "",
    }
    return render(request, "registration/login.html", context)


@require_http_methods(["GET", "POST"])
def signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = SignupForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            success_message = "Account created successfully. You can now sign in."
            if _is_ajax(request):
                return JsonResponse(
                    {
                        "success": True,
                        "redirect_url": reverse("user_auth:login"),
                    }
                )
            messages.success(request, success_message)
            return redirect("user_auth:login")

        error_message = "Please correct the highlighted fields and try again."
        if _is_ajax(request):
            return JsonResponse(
                {
                    "success": False,
                    "error": error_message,
                    "field_errors": form.errors.get_json_data(),
                },
                status=400,
            )
        messages.error(request, error_message)

    return render(request, "registration/signup.html", {"form": form})


@require_http_methods(["GET", "POST"])
def logout_view(request):
    if request.method == "POST" or request.user.is_authenticated:
        auth_logout(request)
        if _is_ajax(request):
            return JsonResponse(
                {"success": True, "redirect_url": reverse("user_auth:login")}
            )
        messages.info(request, "You have been signed out.")
    return redirect("user_auth:login")


def home_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("user_auth:login")
