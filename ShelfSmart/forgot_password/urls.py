from django.urls import path

from .views import SimpleResetPasswordView

app_name = "forgot_password"

urlpatterns = [
    path("reset/", SimpleResetPasswordView.as_view(), name="reset"),
]
