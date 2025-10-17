from django.shortcuts import render, redirect
from django.contrib import messages
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
        
        # Get role from user_type field in Django User model
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
def book_management(request):
    """Book Management - CRUD operations"""
    try:
        logger.info("[dashboard] book_management %s by user=%s role=%s", request.method, getattr(request, "user", None), getattr(request.user, "role", None))
    except Exception:
        pass
    if request.method == "POST":
        action = request.POST.get("action")
        # Only admins can mutate
        user_type = getattr(request.user, "user_type", "user")
        if user_type != "admin":
            messages.error(request, "You do not have permission to modify books.")
            return redirect("/admin-panel/books/")

        try:
            logger.info("[dashboard] POST action=%s data=%s", action, dict(request.POST))
            print("[dashboard] POST action=", action, " data=", dict(request.POST))
            if action == "add":
                # Add new book via ORM
                name = _single_line(request.POST.get("name") or "")
                book_type = _single_line(request.POST.get("type") or "")
                language = _single_line(request.POST.get("language") or "English")
                quantity = int(request.POST.get("quantity") or 1)
                availability = request.POST.get("availability") or "Available"

                if not name or not book_type:
                    messages.error(request, "Name and Type are required fields.")
                    return redirect("/admin-panel/books/")

                book = Book(
                    name=name,
                    type=book_type,
                    language=language,
                    quantity=quantity,
                    availability=availability,
                )
                book.save()
                print("[dashboard] ORM add saved id=", book.id)
                messages.success(request, "Book added successfully!")

            elif action == "edit":
                # Update book via ORM
                book_id = request.POST.get("book_id")
                book = Book.objects.get(pk=book_id)
                
                # Update fields with new schema
                new_name = request.POST.get("name")
                new_type = request.POST.get("type")
                new_language = request.POST.get("language")
                new_quantity = request.POST.get("quantity")
                new_availability = request.POST.get("availability")
                
                if new_name is not None:
                    book.name = _single_line(new_name) or book.name
                if new_type is not None:
                    book.type = _single_line(new_type) or book.type
                if new_language is not None:
                    book.language = _single_line(new_language) or book.language
                if new_quantity is not None:
                    book.quantity = int(new_quantity) if new_quantity else book.quantity
                if new_availability is not None:
                    book.availability = new_availability or book.availability
                    
                book.save()
                print("[dashboard] ORM edit saved id=", book.id)
                messages.success(request, "Book updated successfully!")

            elif action == "delete":
                # Delete book via ORM
                book_id = request.POST.get("book_id")
                print("[dashboard] ORM delete id=", book_id)
                Book.objects.filter(pk=book_id).delete()
                messages.success(request, "Book deleted successfully!")

        except Exception as e:
            logger.exception("[dashboard] Error in book_management mutation: %s", e)
            messages.error(request, f"Error: {str(e)}")

        return redirect("/admin-panel/books/")
    
    # GET request - fetch all books
    try:
        # Fetch all books via ORM
        books_qs = Book.objects.all().order_by("id")
        # Format books data with new schema
        books = []
        for b in books_qs:
            books.append({
                "id": b.id,
                "book_id": b.book_id,  # Alias property
                "name": b.name,
                "type": b.type,
                "language": b.language,
                "quantity": b.quantity,
                "availability": b.availability,
                "created_at": b.created_at,
                "updated_at": b.updated_at,
            })

        context = {
            "user_info": get_current_user_info(request),
            "books": books,
        }
        return render(request, "book_management/book_management.html", context)
    
    except Exception as e:
        messages.error(request, f"Error loading books: {str(e)}")
        return render(request, "book_management/book_management.html", {
            "user_info": get_current_user_info(request),
            "books": []
        })
