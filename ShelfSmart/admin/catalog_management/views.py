from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from user_auth.decorators import admin_required
import logging

from datetime import datetime, date
from admin.common.models import Book, BorrowRecord
from django.contrib.auth import get_user_model
import json

User = get_user_model()

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
def catalog_admin(request):
    """Catalog management - Borrowed and Overdue books"""
    if request.method == "POST":
        action = request.POST.get("action")
        
        try:
            if action == "return":
                # Mark book as returned
                borrow_id = request.POST.get("borrow_id")
                
                # Get the borrow record
                borrow_record = BorrowRecord.objects.select_related('book').get(id=borrow_id)
                
                # Mark as returned
                borrow_record.is_returned = True
                borrow_record.return_date = date.today()
                borrow_record.save()
                
                # Update book quantity and availability
                book = borrow_record.book
                book.quantity += 1
                if book.quantity > 0:
                    book.availability = "Available"
                book.save()
                
                messages.success(request, "Book marked as returned successfully!")
                logger.info(f"Admin returned book {book.name} for user {borrow_record.user_id}")
                
        except BorrowRecord.DoesNotExist:
            messages.error(request, "Borrow record not found.")
        except Exception as e:
            logger.error(f"Error returning book: {str(e)}")
            messages.error(request, f"Error: {str(e)}")
        
        return redirect("/admin-panel/catalog/admin/")
    
    try:
        # Fetch all borrowed books (not returned) with user information
        borrowed_books = BorrowRecord.objects.filter(
            is_returned=False
        ).select_related('book').order_by('-borrowed_date')
        
        # Add user information to each record
        borrowed_books_with_users = []
        for record in borrowed_books:
            try:
                user = User.objects.get(id=record.user_id)
                record.user = user  # Attach user object to the record
                borrowed_books_with_users.append(record)
            except User.DoesNotExist:
                # Skip records where user no longer exists
                continue

        # Fetch overdue books with days overdue calculation
        today = date.today()
        overdue_books = BorrowRecord.objects.filter(
            is_returned=False,
            due_date__lt=today
        ).select_related('book').order_by('due_date')
        
        # Add user information and calculate days overdue
        overdue_books_with_users = []
        for record in overdue_books:
            try:
                user = User.objects.get(id=record.user_id)
                record.user = user  # Attach user object to the record
                record.days_overdue = (today - record.due_date).days
                overdue_books_with_users.append(record)
            except User.DoesNotExist:
                continue

        context = {
            "user_info": get_current_user_info(request),
            "borrowed_books": borrowed_books_with_users,
            "overdue_books": overdue_books_with_users,
            "borrowed_count": len(borrowed_books_with_users),
            "overdue_count": len(overdue_books_with_users),
        }

        return render(request, "catalog_management/catalog_admin.html", context)
    
    except Exception as e:
        logger.error(f"Error loading catalog: {str(e)}")
        messages.error(request, f"Error loading catalog: {str(e)}")
        return render(request, "catalog_management/catalog_admin.html", {
            "user_info": get_current_user_info(request),
            "borrowed_books": [],
            "overdue_books": [],
            "borrowed_count": 0,
            "overdue_count": 0,
        })

@admin_required
def student_catalog(request):
    """Student Catalog - View borrowed and returned books"""
    try:
        # Get all borrow records for all users
        all_records = BorrowRecord.objects.select_related('book').order_by('-borrowed_date')
        
        # Add user information to each record
        records_with_users = []
        for record in all_records:
            try:
                user = User.objects.get(id=record.user_id)
                record.user = user  # Attach user object to the record
                records_with_users.append(record)
            except User.DoesNotExist:
                continue
        
        context = {
            "user_info": get_current_user_info(request),
            "borrow_records": records_with_users,
        }
        
        return render(request, "catalog_management/catalog_student.html", context)
    
    except Exception as e:
        logger.error(f"Error loading student catalog: {str(e)}")
        messages.error(request, f"Error loading catalog: {str(e)}")
        return render(request, "catalog_management/catalog_student.html", {
            "user_info": get_current_user_info(request),
            "borrow_records": [],
        })