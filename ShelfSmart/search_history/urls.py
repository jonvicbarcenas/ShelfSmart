from django.urls import path
from . import views

app_name = 'search_history'

urlpatterns = [
    # API endpoints for search history management
    path('api/save/', views.save_search_history, name='save_search_history'),
    path('api/', views.get_search_history, name='get_search_history'),
    path('api/clear/', views.clear_search_history, name='clear_search_history'),
    path('api/delete/<int:item_id>/', views.delete_search_item, name='delete_search_item'),
]
