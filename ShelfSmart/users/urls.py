from django.urls import path, include

app_name = 'users'

urlpatterns = [
    # User Dashboard
    path('dashboard/', include('users.user_dashboard.urls')),
    
    # User Profile
    path('profile/', include('users.user_profile.urls')),
    
    # User Catalog
    path('catalog/', include('users.catalog.urls')),
]
