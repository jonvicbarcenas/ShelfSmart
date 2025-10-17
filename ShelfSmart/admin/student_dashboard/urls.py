from django.urls import path
from . import views

app_name = 'student_dashboard'

urlpatterns = [
    path('', views.student_dashboard, name='dashboard'),
]
