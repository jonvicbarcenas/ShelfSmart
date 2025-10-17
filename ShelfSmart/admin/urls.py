from django.urls import path, include

app_name = 'admin'

urlpatterns = [
    # Admin Dashboard
    path('dashboard/', include('admin.admin_dashboard.urls')),
    
    # Admin Profile
    path('profile/', include('admin.admin_profile.urls')),
    
    # Book Management
    path('books/', include('admin.book_management.urls')),
    
    # User Management
    path('users/', include('admin.user_management.urls')),
    
    # Catalog Management
    path('catalog/', include('admin.catalog_management.urls')),
    
    # Student Dashboard
    path('student-dashboard/', include('admin.student_dashboard.urls')),
    
    # Student Catalog (Profile)
    path('student/', include('admin.student_catalog.urls')),
]
