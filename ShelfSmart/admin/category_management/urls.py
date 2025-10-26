from django.urls import path
from . import views

app_name = 'category_management'

urlpatterns = [
    path('', views.category_management, name='category_management'),
]
