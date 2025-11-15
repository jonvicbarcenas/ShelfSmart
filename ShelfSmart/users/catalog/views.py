from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from user_auth.decorators import user_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from admin.common.models import Book, BorrowRecord, Category
from settings.models import AppSettings
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Create your views here.

@user_required
def catalog_view(request):
    """
    User catalog view - displays available books for borrowing with category filtering and sorting
    """
    # Get category filter from query params
    category_id = request.GET.get('category', None)
    
    # Get sort parameter from query params
    sort_by = request.GET.get('sort', '-created_at')
    
    # Validate sort parameter to prevent injection attacks
    allowed_sort_fields = [
        'title', '-title',
        'created_at', '-created_at',
        'category__category_name', '-category__category_name',
        'publisher__publisher_name', '-publisher__publisher_name'
    ]
    
    if sort_by not in allowed_sort_fields:
        sort_by = '-created_at'  # Default to newest first
    
    # Fetch books with related category, publisher, and author data
    books_query = Book.objects.select_related('category', 'publisher').prefetch_related(
        'book_authors__author'
    ).all()
    
    # Apply category filter if provided
    if category_id:
        try:
            books_query = books_query.filter(category_id=category_id)
        except ValueError:
            pass  # Invalid category ID, show all books
    
    # Apply sorting
    books_qs = books_query.order_by(sort_by)
    
    # Add dynamic availability for each book based on current user
    books = []
    for book in books_qs:
        # Add dynamic availability as an attribute
        book.user_availability = book.get_user_availability(request.user)
        books.append(book)
    
    # Fetch all categories for the filter dropdown
    categories = Category.objects.all().order_by('category_name')
    
    user_info = {
        'full_name': f"{request.user.first_name} {request.user.last_name}",
        'role': request.user.get_user_type_display(),
        'username': request.user.username
    }
    context = {
        'user': request.user,
        'user_info': user_info,
        'books': books,
        'categories': categories,
        'selected_category': category_id,
        'selected_sort': sort_by,
    }
    return render(request, 'catalog/catalog.html', context)

@user_required
@require_http_methods(["POST"])
def borrow_book(request, book_id):
    """
    Handle book borrowing request
    """
    try:
        # Get the book
        book = Book.objects.get(id=book_id)
        
        # Check if book is available for this specific user
        user_availability = book.get_user_availability(request.user)
        if user_availability != 'available':
            if user_availability == 'unavailable':
                message = 'No copies of this book are available.'
            elif user_availability == 'borrowed':
                message = 'You have already borrowed this book and not returned it yet.'
            else:
                message = 'This book is currently not available for borrowing.'
            
            return JsonResponse({
                'success': False,
                'message': message
            }, status=400)
        
        # Create borrow record
        # Get default borrow days from settings
        app_settings = AppSettings.get_settings()
        borrow_days = app_settings.default_borrow_days
        due_date = datetime.now().date() + timedelta(days=borrow_days)
        
        borrow_record = BorrowRecord.objects.create(
            user_id=request.user.id,
            book=book,
            due_date=due_date,
            is_returned=False
        )
        
        # Update book quantity
        book.quantity -= 1
        if book.quantity == 0:
            book.availability = 'borrowed'
        book.save()
        
        logger.info(f"User {request.user.username} borrowed book {book.title}")
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully borrowed "{book.title}". Due date: {due_date.strftime("%B %d, %Y")}',
            'due_date': due_date.strftime('%Y-%m-%d'),
            'new_quantity': book.quantity,
            'new_availability': book.computed_availability
        })
        
    except Book.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Book not found.'
        }, status=404)
    except Exception as e:
        logger.error(f"Error borrowing book: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while borrowing the book. Please try again.'
        }, status=500)

@user_required
@require_http_methods(["GET"])
def get_book_details(request, book_id):
    """
    API endpoint to fetch complete book details for view popup
    """
    try:
        # Fetch book with related data
        book = Book.objects.select_related('category', 'publisher').prefetch_related(
            'book_authors__author'
        ).get(id=book_id)
        
        # Get authors for this book
        authors = []
        for book_author in book.book_authors.all():
            authors.append({
                'id': book_author.author.id,
                'name': book_author.author.name,
                'role': book_author.author_role
            })
        
        # Build response data - wrap under 'book' key to match JavaScript expectations
        response_data = {
            'success': True,
            'book': {
                'id': book.id,
                'book_id': book.book_id,
                'isbn': book.isbn or '',
                'title': book.title,
                'subtitle': book.subtitle or '',
                'description': book.description or '',
                'category_name': book.category.category_name if book.category else 'N/A',
                'category_id': book.category.id if book.category else None,
                'publisher_name': book.publisher.publisher_name if book.publisher else 'N/A',
                'publisher_id': book.publisher.id if book.publisher else None,
                'authors': authors,
                'publication_date': book.publication_date.strftime('%Y-%m-%d') if book.publication_date else '',
                'edition': book.edition or '',
                'pages': book.pages or 0,
                'language': book.language,
                'quantity': book.quantity,
                'total_copies': book.total_copies,
                'availability': book.availability,
                'cover_image_url': book.cover_image_url or '',
                'created_at': book.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': book.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
        }
        
        logger.info(f"Fetched book details for book ID: {book_id}")
        return JsonResponse(response_data)
        
    except Book.DoesNotExist:
        logger.error(f"Book not found: {book_id}")
        return JsonResponse({
            'success': False,
            'error': 'Book not found.'
        }, status=404)
    except Exception as e:
        logger.error(f"Error fetching book details: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while fetching book details.'
        }, status=500)


@user_required
@require_http_methods(["POST"])
def save_search_history(request):
    """
    API endpoint to save user search history
    """
    try:
        import json
        data = json.loads(request.body)
        
        search_query = data.get('search_query', '').strip()
        search_type = data.get('search_type', 'general')
        results_count = data.get('results_count', 0)
        
        if not search_query:
            return JsonResponse({
                'success': False,
                'message': 'Search query is required.'
            }, status=400)
        
        # Check if this exact search already exists in recent history (last 10 minutes)
        from django.utils import timezone
        ten_minutes_ago = timezone.now() - timedelta(minutes=10)
        
        recent_duplicate = SearchHistory.objects.filter(
            user_id=request.user.id,
            search_query=search_query,
            created_at__gte=ten_minutes_ago
        ).exists()
        
        # Only save if not a recent duplicate
        if not recent_duplicate:
            SearchHistory.objects.create(
                user_id=request.user.id,
                search_query=search_query,
                search_type=search_type,
                results_count=results_count
            )
            logger.info(f"Search history saved for user {request.user.id}: {search_query}")
        
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


@user_required
@require_http_methods(["GET"])
def get_search_history(request):
    """
    API endpoint to retrieve user search history
    """
    try:
        # Get limit from query params (default to 10)
        limit = int(request.GET.get('limit', 10))
        limit = min(limit, 50)  # Cap at 50 to prevent excessive data
        
        # Fetch user's search history
        search_history = SearchHistory.objects.filter(
            user_id=request.user.id
        ).order_by('-created_at')[:limit]
        
        # Build response data
        history_data = []
        for item in search_history:
            history_data.append({
                'id': item.id,
                'search_query': item.search_query,
                'search_type': item.search_type,
                'results_count': item.results_count,
                'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return JsonResponse({
            'success': True,
            'history': history_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching search history: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while fetching search history.'
        }, status=500)


@user_required
@require_http_methods(["DELETE"])
def clear_search_history(request):
    """
    API endpoint to clear user search history
    """
    try:
        # Delete all search history for the current user
        deleted_count = SearchHistory.objects.filter(user_id=request.user.id).delete()[0]
        
        logger.info(f"Cleared {deleted_count} search history entries for user {request.user.id}")
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully cleared {deleted_count} search history entries.'
        })
        
    except Exception as e:
        logger.error(f"Error clearing search history: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while clearing search history.'
        }, status=500)
