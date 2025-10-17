from django.urls import path
from . import views

app_name = 'student_catalog'

urlpatterns = [
    path('profile/', views.student_profile, name='profile'),
]
