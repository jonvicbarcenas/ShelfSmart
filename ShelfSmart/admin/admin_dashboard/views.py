from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from user_auth.decorators import admin_required
import logging

from datetime import datetime, date
from django.db.models import Count, Q
from django.db.models.functions import ExtractMonth, ExtractYear
from user_auth.models import User
from admin.common.models import Book, BorrowRecord
import json

# Configure logging
logger = logging.getLogger(__name__)

def _single_line(value: str) -> str:
    """Normalize input to a single line: remove CR/LF, collapse internal whitespace, and strip."""
    if value is None:
        return ""
    # Replace newlines with space, then collapse multiple spaces
    cleaned = value.replace("\r", " ").replace("\n", " ")
    # Collapse any repeated whitespace
    cleaned = " ".join(cleaned.split())
    return cleaned.strip()

def get_current_user_info(request):
    """Helper function to get current user's info from Django User object and session"""
    # Use Django's authenticated user instead of querying Supabase
    if request.user.is_authenticated:
        user = request.user
        
        # Get names from Django User model
        first_name = user.first_name or "User"
        last_name = user.last_name or ""
        full_name = f"{first_name} {last_name}".strip() if last_name else first_name
        username = user.username or "username"
        
        # Get role directly from Django User model (custom field)
        role = getattr(user, 'user_type', 'user').capitalize()
        
        return {
            "full_name": full_name,
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "role": role
        }
    
    # Fallback if not authenticated
    return {
        "full_name": "User",
        "first_name": "User",
        "last_name": "",
        "username": "username",
        "role": "User"
    }

@admin_required
def dashboard_view(request):
    """Admin Dashboard with real-time data from the database"""
    # Fetch total users from Django's User model
    total_users = User.objects.count()
    logger.info(f"Total users found: {total_users}")

    # Fetch total books from the Book model
    total_books = Book.objects.count()
    logger.info(f"Total books found: {total_books}")

    # Fetch active admins from the User model
    admins = User.objects.filter(user_type='admin')
    logger.info(f"Admins found: {admins.count()}")

    # Fetch borrow statistics from BorrowRecord model
    # Total currently borrowed books (not returned)
    total_borrowed = BorrowRecord.objects.filter(is_returned=False).count()
    logger.info(f"Total borrowed books: {total_borrowed}")
    
    # Total returned books (all time)
    total_returned = BorrowRecord.objects.filter(is_returned=True).count()
    logger.info(f"Total returned books: {total_returned}")
    
    # Fetch overdue borrowers (not returned and due date passed)
    today = date.today()
    overdue_records = BorrowRecord.objects.filter(
        is_returned=False,
        due_date__lt=today
    ).select_related('book').order_by('due_date')
    
    # Build overdue borrowers list with user information
    overdue_borrowers = []
    for record in overdue_records:
        try:
            user = User.objects.get(id=record.user_id)
            days_overdue = (today - record.due_date).days
            overdue_borrowers.append({
                'id': record.id,
                'user_name': f"{user.first_name} {user.last_name}",
                'username': user.username,
                'book_name': record.book.title,
                'due_date': record.due_date,
                'days_overdue': days_overdue
            })
        except User.DoesNotExist:
            continue
    
    logger.info(f"Overdue borrowers found: {len(overdue_borrowers)}")
    
    # Paginate overdue borrowers (3 items per page)
    paginator = Paginator(overdue_borrowers, 3)
    page_number = request.GET.get('page', 1)
    
    try:
        overdue_borrowers_page = paginator.page(page_number)
    except PageNotAnInteger:
        overdue_borrowers_page = paginator.page(1)
    except EmptyPage:
        overdue_borrowers_page = paginator.page(paginator.num_pages)
    
    # Calculate monthly borrow and return statistics for the current year
    current_year = datetime.now().year
    
    # Initialize monthly data arrays (12 months)
    monthly_borrowed = [0] * 12
    monthly_returned = [0] * 12
    
    # Get borrowed books by month (based on borrowed_date)
    borrowed_by_month = BorrowRecord.objects.filter(
        borrowed_date__year=current_year
    ).annotate(
        month=ExtractMonth('borrowed_date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    for item in borrowed_by_month:
        month_index = item['month'] - 1  # Convert 1-12 to 0-11
        monthly_borrowed[month_index] = item['count']
    
    # Get returned books by month (based on return_date)
    returned_by_month = BorrowRecord.objects.filter(
        return_date__year=current_year,
        is_returned=True
    ).annotate(
        month=ExtractMonth('return_date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    for item in returned_by_month:
        month_index = item['month'] - 1  # Convert 1-12 to 0-11
        monthly_returned[month_index] = item['count']
    
    logger.info(f"Monthly borrowed: {monthly_borrowed}")
    logger.info(f"Monthly returned: {monthly_returned}")

    context = {
        "user_info": get_current_user_info(request),
        "total_users": total_users,
        "total_books": total_books,
        "overdue_borrowers": overdue_borrowers_page,
        "total_borrowed": total_borrowed,
        "total_returned": total_returned,
        "monthly_borrowed": json.dumps(monthly_borrowed),
        "monthly_returned": json.dumps(monthly_returned),
        "admins": admins,
    }

    return render(request, "admin_dashboard/admin_dashboard.html", context)
