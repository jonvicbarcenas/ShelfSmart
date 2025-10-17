from django.urls import path
from . import views

app_name = 'catalog_management'

urlpatterns = [
    path('admin/', views.catalog_admin, name='admin'),
    path('student/', views.student_catalog, name='student'),
]
