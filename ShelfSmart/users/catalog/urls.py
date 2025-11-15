from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.catalog_view, name='catalog'),
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('api/book/<int:book_id>/', views.get_book_details, name='get_book_details'),
    # Search history endpoints
    path('api/search-history/save/', views.save_search_history, name='save_search_history'),
    path('api/search-history/', views.get_search_history, name='get_search_history'),
    path('api/search-history/clear/', views.clear_search_history, name='clear_search_history'),
]
