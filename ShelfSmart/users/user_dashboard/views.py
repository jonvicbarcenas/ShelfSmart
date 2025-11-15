from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from user_auth.decorators import user_required
from admin.common.models import BorrowRecord
from settings.models import AppSettings
from datetime import date, timedelta

# Create your views here.

@user_required
def dashboard_view(request):
    """
    User dashboard view - displays user's borrowed books, notifications, etc.
    """
    # Fetch user's borrowed books (not returned yet)
    borrowed_books = BorrowRecord.objects.filter(
        user_id=request.user.id,
        is_returned=False
    ).select_related('book').order_by('-borrowed_date')
    
    # Calculate stats
    borrowed_books_count = borrowed_books.count()
    
    # Count overdue books (due_date < today and not returned)
    today = date.today()
    overdue_books_count = borrowed_books.filter(due_date__lt=today).count()
    
    user_info = {
        'full_name': f"{request.user.first_name} {request.user.last_name}",
        'role': request.user.get_user_type_display(),
        'username': request.user.username
    }
    
    context = {
        'user': request.user,
        'user_info': user_info,
        'borrowed_books': borrowed_books,
        'borrowed_books_count': borrowed_books_count,
        'overdue_books_count': overdue_books_count,
        'today': today,
    }
    return render(request, 'user_dashboard/dashboard.html', context)


@user_required
@require_http_methods(["POST"])
def renew_borrowed_book(request, record_id):
    """
    Renew a borrowed book for the current user by extending its due_date
    by the default_borrow_days, respecting max_renewals.
    """
    try:
        # Get the borrow record that belongs to the user and is not returned
        record = BorrowRecord.objects.select_related('book').get(
            id=record_id,
            user_id=request.user.id,
            is_returned=False
        )

        app_settings = AppSettings.get_settings()

        if record.renewal_count >= app_settings.max_renewals:
            return JsonResponse({
                'success': False,
                'message': 'You have reached the maximum number of renewals for this book.'
            }, status=400)

        # Extend due date
        record.due_date = record.due_date + timedelta(days=app_settings.default_borrow_days)
        record.renewal_count += 1
        record.save()

        return JsonResponse({
            'success': True,
            'message': f'Book renewed successfully. New due date: {record.due_date.strftime("%B %d, %Y")}',
            'new_due_date': record.due_date.strftime('%Y-%m-%d'),
            'renewal_count': record.renewal_count
        })
    except BorrowRecord.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Borrow record not found.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while renewing the book.'
        }, status=500)
