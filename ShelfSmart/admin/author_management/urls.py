from django.urls import path
from . import views

app_name = 'author_management'

urlpatterns = [
    path('', views.author_management, name='author_management'),
]
