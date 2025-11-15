from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta
import json
import logging

from .models import SearchHistory

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["POST"])
def save_search_history(request):
    """
    API endpoint to save user search history
    """
    try:
        data = json.loads(request.body)
        
        search_query = data.get('search_query', '').strip()
        search_type = data.get('search_type', 'general')
        results_count = data.get('results_count', 0)
        search_context = data.get('search_context', 'catalog')
        
        if not search_query:
            return JsonResponse({
                'success': False,
                'message': 'Search query is required.'
            }, status=400)
        
        # Check if this exact search already exists in recent history (last 10 minutes)
        ten_minutes_ago = timezone.now() - timedelta(minutes=10)
        
        recent_duplicate = SearchHistory.objects.filter(
            user=request.user,
            search_query=search_query,
            search_context=search_context,
            created_at__gte=ten_minutes_ago
        ).exists()
        
        # Only save if not a recent duplicate
        if not recent_duplicate:
            SearchHistory.objects.create(
                user=request.user,
                search_query=search_query,
                search_type=search_type,
                results_count=results_count,
                search_context=search_context
            )
            logger.info(f"Search history saved for user {request.user.username}: {search_query}")
        
        return JsonResponse({
            'success': True,
            'message': 'Search history saved successfully.'
        })
        
    except Exception as e:
        logger.error(f"Error saving search history: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while saving search history.'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_search_history(request):
    """
    API endpoint to retrieve user search history
    """
    try:
        # Get parameters from query params
        limit = int(request.GET.get('limit', 10))
        limit = min(limit, 50)  # Cap at 50 to prevent excessive data
        
        search_context = request.GET.get('context', None)
        
        # Build query
        query = SearchHistory.objects.filter(user=request.user)
        
        # Filter by context if provided
        if search_context:
            query = query.filter(search_context=search_context)
        
        # Get search history
        search_history = query.order_by('-created_at')[:limit]
        
        # Build response data
        history_data = []
        for item in search_history:
            history_data.append({
                'id': item.id,
                'search_query': item.search_query,
                'search_type': item.search_type,
                'results_count': item.results_count,
                'search_context': item.search_context,
                'created_at': item.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'history': history_data,
            'total_count': query.count()
        })
        
    except Exception as e:
        logger.error(f"Error fetching search history: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while fetching search history.'
        }, status=500)


@login_required
@require_http_methods(["DELETE"])
def clear_search_history(request):
    """
    API endpoint to clear user search history
    """
    try:
        # Get context filter if provided
        search_context = request.GET.get('context', None)
        
        # Build query
        query = SearchHistory.objects.filter(user=request.user)
        
        # Filter by context if provided
        if search_context:
            query = query.filter(search_context=search_context)
        
        # Delete search history
        deleted_count = query.delete()[0]
        
        logger.info(f"Cleared {deleted_count} search history entries for user {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully cleared {deleted_count} search history entries.',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        logger.error(f"Error clearing search history: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while clearing search history.'
        }, status=500)


@login_required
@require_http_methods(["DELETE"])
def delete_search_item(request, item_id):
    """
    API endpoint to delete a specific search history item
    """
    try:
        # Get the search history item
        search_item = SearchHistory.objects.get(
            id=item_id,
            user=request.user  # Ensure user can only delete their own items
        )
        
        search_item.delete()
        
        logger.info(f"Deleted search history item {item_id} for user {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'message': 'Search history item deleted successfully.'
        })
        
    except SearchHistory.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Search history item not found.'
        }, status=404)
    except Exception as e:
        logger.error(f"Error deleting search history item: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while deleting the search history item.'
        }, status=500)
