from django.shortcuts import render
from user_auth.decorators import user_required
from admin.common.models import BorrowRecord
from datetime import date, timedelta


@user_required
def notifications_view(request):
    """
    User notifications view - displays user's notifications for overdue and due soon books.
    """
    today = date.today()
    due_soon_threshold = today + timedelta(days=3)  # Books due within 3 days
    
    # Fetch user's borrowed books (not returned yet)
    borrowed_books = BorrowRecord.objects.filter(
        user_id=request.user.id,
        is_returned=False
    ).select_related('book').order_by('due_date')
    
    # Categorize notifications
    overdue_books = borrowed_books.filter(due_date__lt=today)
    due_today_books = borrowed_books.filter(due_date=today)
    due_soon_books = borrowed_books.filter(
        due_date__gt=today,
        due_date__lte=due_soon_threshold
    )
    
    # Calculate stats for header
    total_notifications = overdue_books.count() + due_today_books.count() + due_soon_books.count()
    
    user_info = {
        'full_name': f"{request.user.first_name} {request.user.last_name}",
        'role': request.user.get_user_type_display(),
        'username': request.user.username
    }
    
    context = {
        'user': request.user,
        'user_info': user_info,
        'overdue_books': overdue_books,
        'due_today_books': due_today_books,
        'due_soon_books': due_soon_books,
        'total_notifications': total_notifications,
        'today': today,
    }
    return render(request, 'notifications/notifications.html', context)
