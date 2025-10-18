from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.catalog_view, name='catalog'),
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
]
