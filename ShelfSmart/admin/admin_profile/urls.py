from django.urls import path
from . import views

app_name = 'admin_profile'

urlpatterns = [
    path('', views.admin_profile, name='profile'),
]
