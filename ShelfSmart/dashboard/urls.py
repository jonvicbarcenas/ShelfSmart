from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('userborrow/', views.userborrow, name='userborrow'),
    path("catalog_admin/", views.catalog_admin, name="catalog_admin"),
    path("book_management/", views.book_management, name="book_management"),
    path("user_management/", views.user_management, name="user_management"),
    path("user_borrow/", views.userborrow, name="user_borrow"),
    path("admin_profile/", views.admin_profile, name="admin_profile"),
    path("student_profile/", views.student_profile, name="student_profile"),
]