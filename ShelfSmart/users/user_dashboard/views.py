from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from user_auth.decorators import user_required
from admin.common.models import BorrowRecord
from datetime import date

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
