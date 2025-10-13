from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import logging
import traceback

from .decorators import admin_required
from dashboard.models import Book

logger = logging.getLogger(__name__)


@login_required
def book_list(request):
    """List books. All authenticated users can view. Non-admins see read-only UI."""
    try:
        logger.info("[books_admin] book_list called by user=%s role=%s", request.user, getattr(request.user, "role", None))
    except Exception:
        pass
    try:
        print("[books_admin] book_list reached; count=", Book.objects.count())
    except Exception:
        pass
    books = Book.objects.all().order_by("id")
    is_admin = getattr(request.user, "role", "user") == "admin"
    return render(request, "books_admin/list.html", {"books": books, "is_admin": is_admin})


@admin_required
def book_create(request):
    """Create a new book (admin only)."""
    logger.info("[books_admin] book_create %s by user=%s", request.method, getattr(request, "user", None))
    print("[books_admin] book_create entered method=", request.method)
    if request.method == "POST":
        try:
            logger.info("[books_admin] POST data: %s", dict(request.POST))
            print("[books_admin] POST data =", dict(request.POST))
            title = request.POST.get("title")
            author = request.POST.get("author") or "Unknown"
            type_ = request.POST.get("type") or ""
            language = request.POST.get("language") or ""
            total_copies = int(request.POST.get("total_copies") or 1)
            available_copies = int(request.POST.get("available_copies") or 1)

            book = Book(
                title=title,
                author=author,
            )
            # If your Book model has 'type' and 'language' columns in DB via Supabase only,
            # they won't exist in Django ORM. We'll ignore them in ORM, but keep fields in the form for future use.
            book.total_copies = total_copies
            book.available_copies = available_copies
            book.save()
            print("[books_admin] book saved with id=", book.id)

            messages.success(request, "Book created successfully.")
            return redirect("books_admin:list")
        except Exception as e:
            logger.error("[books_admin] Error creating book: %s", e)
            traceback.print_exc()
            messages.error(request, f"Error creating book: {e}")

    return render(request, "books_admin/form.html", {"mode": "create"})


@admin_required
def book_update(request, pk: int):
    """Update an existing book (admin only)."""
    logger.info("[books_admin] book_update %s for pk=%s by user=%s", request.method, pk, getattr(request, "user", None))
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        try:
            logger.info("[books_admin] POST data: %s", dict(request.POST))
            print("[books_admin] update POST data =", dict(request.POST))
            book.title = request.POST.get("title")
            book.author = request.POST.get("author") or "Unknown"
            # type and language ignored if not present on ORM model
            book.total_copies = int(request.POST.get("total_copies") or book.total_copies or 1)
            book.available_copies = int(request.POST.get("available_copies") or book.available_copies or 1)
            book.save()
            print("[books_admin] book updated id=", book.id)

            messages.success(request, "Book updated successfully.")
            return redirect("books_admin:list")
        except Exception as e:
            logger.error("[books_admin] Error updating book %s: %s", pk, e)
            traceback.print_exc()
            messages.error(request, f"Error updating book: {e}")

    return render(request, "books_admin/form.html", {"mode": "update", "book": book})


@admin_required
def book_delete(request, pk: int):
    """Delete a book (admin only)."""
    logger.info("[books_admin] book_delete %s for pk=%s by user=%s", request.method, pk, getattr(request, "user", None))
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        try:
            print("[books_admin] deleting id=", book.id)
            book.delete()
            messages.success(request, "Book deleted successfully.")
            return redirect("books_admin:list")
        except Exception as e:
            logger.error("[books_admin] Error deleting book %s: %s", pk, e)
            traceback.print_exc()
            messages.error(request, f"Error deleting book: {e}")

    return render(request, "books_admin/confirm_delete.html", {"book": book})

# Create your views here.
