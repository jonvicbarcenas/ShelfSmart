from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import logging

from datetime import datetime, date
from admin.common.supabase_client import supabase
import json
from admin.common.models import Book

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

@login_required
def dashboard_view(request):
    """Admin Dashboard with real-time data from Supabase"""
    try:
        # Fetch total users
        users_response = supabase.table("dashboard_user").select("*").execute()
        total_users = len(users_response.data) if users_response.data else 0

        # Fetch total books
        books_response = supabase.table("dashboard_book").select("*").execute()
        total_books = len(books_response.data) if books_response.data else 0

        # Fetch overdue borrowers
        today = date.today().isoformat()
        overdue_response = supabase.table("dashboard_borrowrecord")\
            .select("*, users:dashboard_user(name, id), books:dashboard_book(title)")\
            .lt("due_date", today)\
            .eq("is_returned", False)\
            .execute()
        
        # Fetch borrowed books stats for chart
        borrowed_response = supabase.table("dashboard_borrowrecord")\
            .select("*")\
            .eq("is_returned", False)\
            .execute()
        
        returned_response = supabase.table("dashboard_borrowrecord")\
            .select("*")\
            .eq("is_returned", True)\
            .execute()
        
        # Fetch active admins
        admins_response = supabase.table("dashboard_user")\
            .select("*")\
            .eq("role", "admin")\
            .execute()

        context = {
            "user_info": get_current_user_info(request),
            "total_users": total_users,
            "total_books": total_books,
            "overdue_borrowers": overdue_response.data if overdue_response.data else [],
            "total_borrowed": len(borrowed_response.data) if borrowed_response.data else 0,
            "total_returned": len(returned_response.data) if returned_response.data else 0,
            "admins": admins_response.data if admins_response.data else [],
        }

        return render(request, "admin_dashboard/admin_dashboard.html", context)
    
    except Exception as e:
        messages.error(request, f"Error loading dashboard: {str(e)}")
        return render(request, "admin_dashboard/admin_dashboard.html", {
            "user_info": get_current_user_info(request),
            "total_users": 0,
            "total_books": 0,
            "overdue_borrowers": [],
            "total_borrowed": 0,
            "total_returned": 0,
            "admins": [],
        })
