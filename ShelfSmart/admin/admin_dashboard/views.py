from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from user_auth.decorators import admin_required
import logging

from datetime import datetime, date
from user_auth.models import User
from admin.common.models import Book

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

    # NOTE: The following sections for overdue borrowers and borrowed/returned stats
    # are placeholders and will be migrated in a future step.
    overdue_borrowers = []
    total_borrowed = 0
    total_returned = 0

    context = {
        "user_info": get_current_user_info(request),
        "total_users": total_users,
        "total_books": total_books,
        "overdue_borrowers": overdue_borrowers,
        "total_borrowed": total_borrowed,
        "total_returned": total_returned,
        "admins": admins,
    }

    return render(request, "admin_dashboard/admin_dashboard.html", context)
