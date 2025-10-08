from __future__ import annotations

from typing import Any, Dict

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from .forms import UsernameResetForm


class SimpleResetPasswordView(View):
    template_name = "forgot_password/reset_password.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = UsernameResetForm()
        return render(request, self.template_name, self._build_context(form))

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = UsernameResetForm(request.POST)

        if form.is_valid():
            form.save()
            success_response = {
                "success": True,
                "redirect_url": reverse("user_auth:login"),
            }
            if self._is_ajax(request):
                return JsonResponse(success_response)
            return redirect(success_response["redirect_url"])

        if self._is_ajax(request):
            return JsonResponse(
                {
                    "success": False,
                    "error": "Please correct the errors below.",
                    "field_errors": form.errors.get_json_data(),
                },
                status=400,
            )

        return render(request, self.template_name, self._build_context(form), status=400)

    def _build_context(self, form: UsernameResetForm) -> Dict[str, Any]:
        return {
            "form": form,
            "login_url": reverse("user_auth:login"),
            "back_url": reverse("user_auth:login"),
            "form_action": reverse("forgot_password:reset"),
        }

    @staticmethod
    def _is_ajax(request: HttpRequest) -> bool:
        return request.headers.get("x-requested-with") == "XMLHttpRequest"
