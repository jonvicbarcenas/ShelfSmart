from django.urls import path
from . import views

app_name = 'book_management'

urlpatterns = [
    path('', views.book_management, name='management'),
    path('api/book/<int:book_id>/', views.get_book_details, name='get_book_details'),
]
