from __future__ import annotations

from typing import Any, Dict, Tuple

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View

from .forms import UsernameResetForm
from .models import PasswordResetOTP


UserModel = get_user_model()


class SimpleResetPasswordView(View):
    template_name = "forgot_password/reset_password.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = UsernameResetForm()
        return render(request, self.template_name, self._build_context(form))

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if "send_otp" in request.POST:
            return self._handle_send_otp(request)

        form = UsernameResetForm(request.POST)

        if form.is_valid():
            form.save()
            success_response = {
                "success": True,
                "redirect_url": reverse("user_auth:login"),
                "message": "Password reset successful. You can now sign in with your new password.",
            }
            if self._is_ajax(request):
                return JsonResponse(success_response)
            messages.success(request, success_response["message"])
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

    def _handle_send_otp(self, request: HttpRequest) -> HttpResponse:
        username = request.POST.get("username", "").strip()

        if not username:
            error_payload = self._build_otp_error("Please provide your username to receive an OTP.")
            return self._respond_otp(error_payload, status=400, request=request)

        try:
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            error_payload = self._build_otp_error("No account found with that username.")
            return self._respond_otp(error_payload, status=404, request=request)

        otp_instance = PasswordResetOTP.objects.create_for_user(user)
        self._send_otp_email(user.email, otp_instance.code)

        success_payload = {
            "success": True,
            "message": "OTP has been sent to your registered email address.",
            "expires_at": timezone.localtime(otp_instance.expires_at).isoformat(),
        }
        return self._respond_otp(success_payload, request=request)

    def _send_otp_email(self, email: str, code: str) -> None:
        if not email:
            return

        subject = "ShelfSmart Password Reset OTP"
        message = (
            "Hello,\n\n"
            "We received a request to reset your password for ShelfSmart. "
            f"Use the following One-Time Password (OTP) to continue: {code}\n\n"
            "This OTP will expire in 10 minutes. If you did not request this change, "
            "please ignore this email.\n\n"
            "Thank you,\n"
            "ShelfSmart Team"
        )

        send_mail(subject=subject, message=message, from_email=None, recipient_list=[email], fail_silently=False)

    def _respond_otp(self, payload: Dict[str, Any], request: HttpRequest, *, status: int = 200) -> HttpResponse:
        if self._is_ajax(request):
            return JsonResponse(payload, status=status)

        if payload.get("success"):
            messages.success(request, payload["message"])
        else:
            messages.error(request, payload["message"])

        return redirect(reverse("forgot_password:reset"))

    @staticmethod
    def _is_ajax(request: HttpRequest) -> bool:
        return request.headers.get("x-requested-with") == "XMLHttpRequest"

    @staticmethod
    def _build_otp_error(message: str) -> Dict[str, Any]:
        return {"success": False, "message": message}
