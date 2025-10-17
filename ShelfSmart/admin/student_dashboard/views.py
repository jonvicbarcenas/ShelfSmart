from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import logging

from datetime import datetime, date
from admin.common.supabase_client import supabase
import json
from admin.common.models import Book

logger = logging.getLogger(__name__)

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
        role = getattr(user, 'role', 'user').capitalize()
        
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
def student_dashboard(request):
    """Student dashboard view"""
    # Get student ID from session
    student_id = request.session.get('user_id', 1)
    
    try:
        # Get student name
        student = supabase.table("dashboard_user").select("name").eq("id", student_id).execute()
        student_name = student.data[0].get("name", "Student") if student.data else "Student"
        
        # Count borrowed books (not returned)
        borrowed_response = supabase.table("dashboard_borrowrecord")\
            .select("*")\
            .eq("user_id", student_id)\
            .eq("is_returned", False)\
            .execute()
        total_borrowed = len(borrowed_response.data) if borrowed_response.data else 0
        
        # Count returned books
        returned_response = supabase.table("dashboard_borrowrecord")\
            .select("*")\
            .eq("user_id", student_id)\
            .eq("is_returned", True)\
            .execute()
        total_returned = len(returned_response.data) if returned_response.data else 0
        
        # Count overdue books
        today = date.today().isoformat()
        overdue_response = supabase.table("dashboard_borrowrecord")\
            .select("*")\
            .eq("user_id", student_id)\
            .lt("due_date", today)\
            .eq("is_returned", False)\
            .execute()
        total_overdue = len(overdue_response.data) if overdue_response.data else 0
        
        # Get recent activities (last 5 borrow records)
        recent_response = supabase.table("dashboard_borrowrecord")\
            .select("*, books:dashboard_book(title, id)")\
            .eq("user_id", student_id)\
            .order("borrowed_date", desc=True)\
            .limit(5)\
            .execute()
        
        recent_activities = []
        if recent_response.data:
            from datetime import datetime
            for record in recent_response.data:
                if record.get('is_returned'):
                    status = 'returned'
                elif record.get('due_date') and record['due_date'] < today:
                    status = 'overdue'
                else:
                    status = 'active'
                
                recent_activities.append({
                    'books': {'title': record.get('books', {}).get('title', 'Unknown Book')},
                    'borrowed_date': record.get('borrowed_date'),
                    'status': status
                })
        
        context = {
            'user_name': student_name,
            'total_borrowed': total_borrowed,
            'total_returned': total_returned,
            'total_overdue': total_overdue,
            'recent_activities': recent_activities,
        }
        
        return render(request, 'student_dashboard/student_dashboard.html', context)
        
    except Exception as e:
        # Handle any errors gracefully
        messages.error(request, f"Error loading dashboard: {str(e)}")
        context = {
            'user_name': 'Student',
            'total_borrowed': 0,
            'total_returned': 0,
            'total_overdue': 0,
            'recent_activities': [],
        }
        return render(request, 'student_dashboard/student_dashboard.html', context)
