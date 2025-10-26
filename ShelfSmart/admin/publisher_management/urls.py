from django.urls import path
from . import views

app_name = 'publisher_management'

urlpatterns = [
    path('', views.publisher_management, name='publisher_management'),
]
