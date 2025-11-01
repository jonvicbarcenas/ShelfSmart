import requests
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from admin.common.models import Category, Publisher, Author

logger = logging.getLogger(__name__)

@require_http_methods(["POST"])
@csrf_exempt
def validate_isbn(request):
    """
    Validate ISBN using Google Books API and return book details.
    
    Expected POST data:
    - isbn: The ISBN number to validate (10 or 13 digits)
    
    Returns:
    - JSON response with book details or error message
    """
    try:
        import json
        data = json.loads(request.body)
        isbn = data.get('isbn', '').strip()
        
        if not isbn:
            return JsonResponse({
                'success': False,
                'error': 'ISBN is required'
            }, status=400)
        
        # Remove any hyphens or spaces from ISBN
        isbn = isbn.replace('-', '').replace(' ', '')
        
        # Validate ISBN format (10 or 13 digits)
        if not (isbn.isdigit() and (len(isbn) == 10 or len(isbn) == 13)):
            return JsonResponse({
                'success': False,
                'error': 'Invalid ISBN format. ISBN must be 10 or 13 digits.'
            }, status=400)
        
        # Call Google Books API
        api_url = f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}'
        logger.info(f'Calling Google Books API: {api_url}')
        
        response = requests.get(api_url, timeout=10)
        
        if response.status_code != 200:
            logger.error(f'Google Books API error: {response.status_code}')
            return JsonResponse({
                'success': False,
                'error': 'Failed to connect to Google Books API'
            }, status=500)
        
        api_data = response.json()
        
        # Check if book was found
        if api_data.get('totalItems', 0) == 0:
            return JsonResponse({
                'success': False,
                'error': 'No book found with this ISBN'
            }, status=404)
        
        # Extract book information
        book_item = api_data['items'][0]
        volume_info = book_item.get('volumeInfo', {})
        
        # Extract relevant fields from API
        api_categories = volume_info.get('categories', [])
        api_publisher = volume_info.get('publisher', '')
        api_authors = volume_info.get('authors', [])
        
        # Query database for matching categories, publishers, and authors
        matched_category_id = None
        matched_publisher_id = None
        matched_author_ids = []
        
        # Match Category: Try to find existing category by name (case-insensitive)
        if api_categories:
            for cat_name in api_categories:
                category = Category.objects.filter(
                    Q(category_name__iexact=cat_name) | Q(category_name__icontains=cat_name)
                ).first()
                if category:
                    matched_category_id = category.id
                    logger.info(f'Matched category: {category.category_name} (ID: {category.id})')
                    break
        
        # Match Publisher: Try to find existing publisher by name (case-insensitive)
        if api_publisher:
            publisher = Publisher.objects.filter(
                Q(publisher_name__iexact=api_publisher) | Q(publisher_name__icontains=api_publisher)
            ).first()
            if publisher:
                matched_publisher_id = publisher.id
                logger.info(f'Matched publisher: {publisher.publisher_name} (ID: {publisher.id})')
        
        # Match Authors: Try to find existing authors by name (case-insensitive)
        if api_authors:
            for author_name in api_authors:
                author = Author.objects.filter(
                    Q(name__iexact=author_name) | Q(name__icontains=author_name)
                ).first()
                if author:
                    matched_author_ids.append({
                        'id': author.id,
                        'name': author.name
                    })
                    logger.info(f'Matched author: {author.name} (ID: {author.id})')
        
        # Build response with both API data and matched DB IDs
        book_data = {
            'success': True,
            'isbn': isbn,
            'title': volume_info.get('title', ''),
            'subtitle': volume_info.get('subtitle', ''),
            'authors': api_authors,
            'publisher': api_publisher,
            'publishedDate': volume_info.get('publishedDate', ''),
            'description': volume_info.get('description', ''),
            'pageCount': volume_info.get('pageCount', 0),
            'categories': api_categories,
            'language': volume_info.get('language', ''),
            'imageLinks': volume_info.get('imageLinks', {}),
            'industryIdentifiers': volume_info.get('industryIdentifiers', []),
            # Database matches
            'matched_category_id': matched_category_id,
            'matched_publisher_id': matched_publisher_id,
            'matched_author_ids': matched_author_ids,
        }
        
        logger.info(f'Successfully validated ISBN: {isbn}')
        return JsonResponse(book_data)
        
    except requests.exceptions.Timeout:
        logger.error('Google Books API timeout')
        return JsonResponse({
            'success': False,
            'error': 'Request timeout. Please try again.'
        }, status=504)
    
    except requests.exceptions.RequestException as e:
        logger.error(f'Request error: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': 'Network error. Please check your connection.'
        }, status=500)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid request data'
        }, status=400)
    
    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred'
        }, status=500)
