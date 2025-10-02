from django.urls import path

from . import views

app_name = "logout_app"

urlpatterns = [
    path("", views.logout_view, name="logout"),
]
