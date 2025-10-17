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
def catalog_admin(request):
    """Catalog management - Borrowed and Overdue books"""
    if request.method == "POST":
        action = request.POST.get("action")
        
        try:
            if action == "return":
                # Mark book as returned
                borrow_id = request.POST.get("borrow_id")
                from datetime import date
                
                # Update borrow record
                supabase.table("dashboard_borrowrecord").update({
                    "is_returned": True,
                    "return_date": date.today().isoformat()
                }).eq("id", borrow_id).execute()
                
                # Get the book_id to update availability
                borrow_record = supabase.table("dashboard_borrowrecord")\
                    .select("book_id")\
                    .eq("id", borrow_id)\
                    .execute()
                
                if borrow_record.data:
                    book_id = borrow_record.data[0]['book_id']
                    
                    # Update book availability
                    book = supabase.table("dashboard_book").select("available_copies").eq("id", book_id).execute()
                    if book.data:
                        new_available = book.data[0]['available_copies'] + 1
                        supabase.table("dashboard_book").update({
                            "available_copies": new_available,
                            "availability": "Available"
                        }).eq("id", book_id).execute()
                
                messages.success(request, "Book marked as returned successfully!")
                
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
        
        return redirect("/admin-panel/catalog/admin/")
    
    try:
        # Fetch borrowed books
        borrowed_books = supabase.table("dashboard_borrowrecord")\
            .select("*, users:dashboard_user(name, id), books:dashboard_book(title, id)")\
            .eq("is_returned", False)\
            .execute()

        # Fetch overdue books with days overdue calculation
        today = date.today().isoformat()
        overdue_books = supabase.table("dashboard_borrowrecord")\
            .select("*, users:dashboard_user(name, id), books:dashboard_book(title, id)")\
            .lt("due_date", today)\
            .eq("is_returned", False)\
            .execute()
        
        # Calculate days overdue for each record
        from datetime import datetime
        for record in overdue_books.data if overdue_books.data else []:
            due_date = datetime.fromisoformat(record['due_date'])
            days_overdue = (datetime.now() - due_date).days
            record['days_overdue'] = days_overdue

        context = {
            "user_info": get_current_user_info(request),
            "borrowed_books": borrowed_books.data if borrowed_books.data else [],
            "overdue_books": overdue_books.data if overdue_books.data else [],
        }

        return render(request, "catalog_management/catalog_admin.html", context)
    
    except Exception as e:
        messages.error(request, f"Error loading catalog: {str(e)}")
        return render(request, "catalog_management/catalog_admin.html", {
            "user_info": get_current_user_info(request),
            "borrowed_books": [],
            "overdue_books": [],
        })

@login_required
def student_catalog(request):
    """Student Catalog - View borrowed and returned books"""
    # Get student ID from session
    student_id = request.session.get('user_id', 1)
    
    if request.method == "POST":
        action = request.POST.get("action")
        
        try:
            if action == "return":
                # Mark book as returned
                borrow_id = request.POST.get("book_id")
                
                # Update borrow record
                supabase.table("dashboard_borrowrecord").update({
                    "is_returned": True,
                    "return_date": date.today().isoformat()
                }).eq("id", borrow_id).eq("user_id", student_id).execute()
                
                # Get the book_id to update availability
                borrow_record = supabase.table("dashboard_borrowrecord")\
                    .select("book_id")\
                    .eq("id", borrow_id)\
                    .execute()
                
                if borrow_record.data:
                    book_id = borrow_record.data[0]['book_id']
                    
                    # Update book availability
                    book = supabase.table("dashboard_book").select("available_copies").eq("id", book_id).execute()
                    if book.data:
                        new_available = book.data[0]['available_copies'] + 1
                        supabase.table("dashboard_book").update({
                            "available_copies": new_available,
                            "availability": "Available"
                        }).eq("id", book_id).execute()
                
                messages.success(request, "Book returned successfully!")
                
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
        
        return redirect("/admin-panel/catalog/student/")
    
    # GET request - fetch student's borrowed and returned books
    try:
        # Fetch borrowed books for this student - FIXED VERSION
        borrowed_books = supabase.table("dashboard_borrowrecord")\
            .select("*, books:dashboard_book(title, id)")\
            .eq("user_id", student_id)\
            .eq("is_returned", False)\
            .execute()
        
        # Fetch returned books for this student - FIXED VERSION
        returned_books = supabase.table("dashboard_borrowrecord")\
            .select("*, books:dashboard_book(title, id)")\
            .eq("user_id", student_id)\
            .eq("is_returned", True)\
            .execute()
        
        # Get student name
        student = supabase.table("dashboard_user").select("name").eq("id", student_id).execute()
        student_name = student.data[0].get("name", "Student") if student.data else "Student"
        
        context = {
            "user_name": student_name,
            "borrowed_books": borrowed_books.data if borrowed_books.data else [],
            "returned_books": returned_books.data if returned_books.data else [],
        }
        
        return render(request, "catalog_management/catalog_student.html", context)
    
    except Exception as e:
        messages.error(request, f"Error loading catalog: {str(e)}")
        return render(request, "catalog_management/catalog_student.html", {
            "user_name": "Student",
            "borrowed_books": [],
            "returned_books": [],
        })
