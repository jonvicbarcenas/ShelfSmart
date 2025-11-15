from django.urls import path
from . import views

app_name = 'due_notifications'

urlpatterns = [
    path('send-due-reminders/', views.send_due_reminders, name='send_due_reminders'),
    path('send-overdue-notifications/', views.send_overdue_notifications, name='send_overdue_notifications'),
]
