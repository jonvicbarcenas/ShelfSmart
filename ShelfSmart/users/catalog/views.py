from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from user_auth.decorators import user_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from admin.common.models import Book, BorrowRecord
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Create your views here.

@user_required
def catalog_view(request):
    """
    User catalog view - displays available books for borrowing
    """
    # Fetch all books from database
    books = Book.objects.all().order_by('-created_at')
    
    user_info = {
        'full_name': f"{request.user.first_name} {request.user.last_name}",
        'role': request.user.get_user_type_display(),
        'username': request.user.username
    }
    context = {
        'user': request.user,
        'user_info': user_info,
        'books': books,
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
        
        # Check if book is available
        if book.availability != 'Available':
            return JsonResponse({
                'success': False,
                'message': 'This book is currently not available for borrowing.'
            }, status=400)
        
        # Check if book has quantity available
        if book.quantity <= 0:
            return JsonResponse({
                'success': False,
                'message': 'No copies of this book are available.'
            }, status=400)
        
        # Check if user already has an active borrow record for this book
        existing_borrow = BorrowRecord.objects.filter(
            user_id=request.user.id,
            book=book,
            is_returned=False
        ).exists()
        
        if existing_borrow:
            return JsonResponse({
                'success': False,
                'message': 'You have already borrowed this book and not returned it yet.'
            }, status=400)
        
        # Create borrow record
        # Due date is 14 days from today
        due_date = datetime.now().date() + timedelta(days=14)
        
        borrow_record = BorrowRecord.objects.create(
            user_id=request.user.id,
            book=book,
            due_date=due_date,
            is_returned=False
        )
        
        # Update book quantity
        book.quantity -= 1
        if book.quantity == 0:
            book.availability = 'Borrowed'
        book.save()
        
        logger.info(f"User {request.user.username} borrowed book {book.name}")
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully borrowed "{book.name}". Due date: {due_date.strftime("%B %d, %Y")}',
            'due_date': due_date.strftime('%Y-%m-%d'),
            'new_quantity': book.quantity,
            'new_availability': book.availability
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
