from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('userborrow/', views.userborrow, name='userborrow'),
    path("catalog_admin/", views.catalog_admin, name="catalog_admin"),
    path("book_management/", views.book_management, name="book_management"),
    path("user_management/", views.user_management, name="user_management"),
]