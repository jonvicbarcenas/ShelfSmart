from django.urls import path
from . import views

app_name = 'user_management'

urlpatterns = [
    path('', views.user_management, name='management'),
]
