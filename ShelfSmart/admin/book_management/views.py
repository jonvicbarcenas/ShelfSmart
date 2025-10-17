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
def book_management(request):
    """Book Management - CRUD operations"""
    try:
        logger.info("[dashboard] book_management %s by user=%s role=%s", request.method, getattr(request, "user", None), getattr(request.user, "role", None))
    except Exception:
        pass
    if request.method == "POST":
        action = request.POST.get("action")
        # Only admins can mutate
        role = getattr(request.user, "role", "user")
        if role != "admin":
            messages.error(request, "You do not have permission to modify books.")
            return redirect("/admin-panel/books/")

        try:
            logger.info("[dashboard] POST action=%s data=%s", action, dict(request.POST))
            print("[dashboard] POST action=", action, " data=", dict(request.POST))
            if action == "add":
                # Add new book via ORM
                title = _single_line(request.POST.get("title") or request.POST.get("name"))
                author = _single_line(request.POST.get("author") or "Unknown")
                total_copies = int(request.POST.get("total_copies") or 1)
                available_copies = int(request.POST.get("available_copies") or total_copies)

                book = Book(
                    title=title,
                    author=author,
                    total_copies=total_copies,
                    available_copies=available_copies,
                )
                book.save()
                print("[dashboard] ORM add saved id=", book.id)
                messages.success(request, "Book added successfully!")

            elif action == "edit":
                # Update book via ORM
                book_id = request.POST.get("book_id")
                book = Book.objects.get(pk=book_id)
                new_title = request.POST.get("title") or request.POST.get("name")
                new_author = request.POST.get("author")
                if new_title is not None:
                    book.title = _single_line(new_title) or book.title
                if new_author is not None:
                    book.author = _single_line(new_author) or book.author or "Unknown"
                book.total_copies = int(request.POST.get("total_copies") or book.total_copies or 1)
                book.available_copies = int(request.POST.get("available_copies") or book.available_copies or 0)
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
        # Compute availability for display if template expects it
        books = []
        for b in books_qs:
            books.append({
                "id": b.id,
                "title": b.title,
                "author": b.author,
                "total_copies": b.total_copies,
                "available_copies": b.available_copies,
                "availability": "Available" if (b.available_copies or 0) > 0 else "Borrowed",
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
