from django.urls import path
from . import views

app_name = 'user_dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('renew/<int:record_id>/', views.renew_borrowed_book, name='renew_borrowed_book'),
]
