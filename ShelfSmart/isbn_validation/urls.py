from django.urls import path
from . import views

app_name = 'isbn_validation'

urlpatterns = [
    path('validate/', views.validate_isbn, name='validate_isbn'),
]
