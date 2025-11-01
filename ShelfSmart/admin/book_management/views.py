from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from user_auth.decorators import admin_required
import logging

from datetime import datetime, date
import json
from admin.common.models import Book, Category, Publisher, Author, BookAuthor

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

@admin_required
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
                # Add new book via ORM with new schema
                title = _single_line(request.POST.get("title") or "")
                isbn = _single_line(request.POST.get("isbn") or "")
                subtitle = _single_line(request.POST.get("subtitle") or "")
                description = _single_line(request.POST.get("description") or "")
                publication_date = request.POST.get("publication_date") or None
                edition = _single_line(request.POST.get("edition") or "")
                pages = request.POST.get("pages")
                language = _single_line(request.POST.get("language") or "English")
                cover_image_url = request.POST.get("cover_image_url") or None
                category_id = request.POST.get("category_id")
                publisher_id = request.POST.get("publisher_id")
                quantity = int(request.POST.get("quantity") or 1)
                total_copies = int(request.POST.get("total_copies") or quantity)
                availability = request.POST.get("availability") or "available"
                
                # Get author data
                author_count = int(request.POST.get("author_count") or 0)

                if not title or not category_id or not publisher_id:
                    messages.error(request, "Title, Category, and Publisher are required fields.")
                    return redirect("/admin-panel/books/")
                
                if author_count == 0:
                    messages.error(request, "At least one author is required.")
                    return redirect("/admin-panel/books/")

                try:
                    category = Category.objects.get(pk=category_id)
                    publisher = Publisher.objects.get(pk=publisher_id)
                    
                    # Create the book
                    book = Book(
                        title=title,
                        isbn=isbn if isbn else None,
                        subtitle=subtitle if subtitle else None,
                        description=description if description else None,
                        publication_date=publication_date if publication_date else None,
                        edition=edition if edition else None,
                        pages=int(pages) if pages else None,
                        language=language,
                        cover_image_url=cover_image_url if cover_image_url else None,
                        category=category,
                        publisher=publisher,
                        quantity=quantity,
                        total_copies=total_copies,
                        availability=availability,
                    )
                    book.save()
                    print("[dashboard] ORM add saved id=", book.id)
                    
                    # Add authors to the book
                    for i in range(author_count):
                        author_id = request.POST.get(f"author_{i}")
                        author_role = request.POST.get(f"author_role_{i}", "primary")
                        
                        if author_id:
                            try:
                                author = Author.objects.get(pk=author_id)
                                BookAuthor.objects.create(
                                    book=book,
                                    author=author,
                                    author_role=author_role
                                )
                            except Author.DoesNotExist:
                                logger.warning(f"Author with id {author_id} not found")
                    
                    messages.success(request, "Book added successfully!")
                except (Category.DoesNotExist, Publisher.DoesNotExist):
                    messages.error(request, "Invalid category or publisher selected.")
                    return redirect("/admin-panel/books/")

            elif action == "edit":
                # Update book via ORM with new schema
                book_id = request.POST.get("book_id")
                book = Book.objects.get(pk=book_id)
                
                # Update fields with new schema
                new_title = request.POST.get("title")
                new_isbn = request.POST.get("isbn")
                new_subtitle = request.POST.get("subtitle")
                new_description = request.POST.get("description")
                new_publication_date = request.POST.get("publication_date")
                new_edition = request.POST.get("edition")
                new_pages = request.POST.get("pages")
                new_language = request.POST.get("language")
                new_cover_image_url = request.POST.get("cover_image_url")
                new_category_id = request.POST.get("category_id")
                new_publisher_id = request.POST.get("publisher_id")
                new_quantity = request.POST.get("quantity")
                new_total_copies = request.POST.get("total_copies")
                
                if new_title is not None:
                    book.title = _single_line(new_title) or book.title
                if new_isbn is not None:
                    book.isbn = _single_line(new_isbn) if new_isbn else None
                if new_subtitle is not None:
                    book.subtitle = _single_line(new_subtitle) if new_subtitle else None
                if new_description is not None:
                    book.description = _single_line(new_description) if new_description else None
                if new_publication_date is not None:
                    book.publication_date = new_publication_date if new_publication_date else None
                if new_edition is not None:
                    book.edition = _single_line(new_edition) if new_edition else None
                if new_pages is not None:
                    book.pages = int(new_pages) if new_pages else None
                if new_language is not None:
                    book.language = _single_line(new_language) or book.language
                if new_cover_image_url is not None:
                    book.cover_image_url = new_cover_image_url if new_cover_image_url else None
                if new_category_id is not None:
                    try:
                        book.category = Category.objects.get(pk=new_category_id)
                    except Category.DoesNotExist:
                        messages.error(request, "Invalid category selected.")
                        return redirect("/admin-panel/books/")
                if new_publisher_id is not None:
                    try:
                        book.publisher = Publisher.objects.get(pk=new_publisher_id)
                    except Publisher.DoesNotExist:
                        messages.error(request, "Invalid publisher selected.")
                        return redirect("/admin-panel/books/")
                if new_quantity is not None:
                    book.quantity = int(new_quantity) if new_quantity else book.quantity
                if new_total_copies is not None:
                    book.total_copies = int(new_total_copies) if new_total_copies else book.total_copies
                    
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
    
    # GET request - fetch all books, categories, publishers, and authors
    try:
        # Fetch all books via ORM with related data
        books_qs = Book.objects.select_related('category', 'publisher').all().order_by("id")
        # Fetch all categories for dropdown
        categories = Category.objects.all().order_by('category_name')
        # Fetch all publishers for dropdown
        publishers = Publisher.objects.all().order_by('publisher_name')
        # Fetch all authors for dropdown
        authors = Author.objects.all().order_by('name')
        
        # Format books data with new schema
        books = []
        for b in books_qs:
            books.append({
                "id": b.id,
                "book_id": b.book_id,  # Alias property
                "title": b.title,
                "isbn": b.isbn or "",
                "subtitle": b.subtitle or "",
                "description": b.description or "",
                "category_id": b.category.id if b.category else None,
                "category_name": b.category.category_name if b.category else "N/A",
                "publisher_id": b.publisher.id if b.publisher else None,
                "publisher_name": b.publisher.publisher_name if b.publisher else "N/A",
                "language": b.language,
                "quantity": b.quantity,
                "total_copies": b.total_copies,
                "availability": b.availability,
                "created_at": b.created_at,
                "updated_at": b.updated_at,
            })

        context = {
            "user_info": get_current_user_info(request),
            "books": books,
            "categories": categories,
            "publishers": publishers,
            "authors": authors,
        }
        return render(request, "book_management/book_management.html", context)
    
    except Exception as e:
        messages.error(request, f"Error loading books: {str(e)}")
        return render(request, "book_management/book_management.html", {
            "user_info": get_current_user_info(request),
            "books": []
        })

@admin_required
def get_book_details(request, book_id):
    """API endpoint to fetch complete book details"""
    try:
        book = Book.objects.select_related('category', 'publisher').get(pk=book_id)
        
        # Get all authors for this book
        book_authors = BookAuthor.objects.filter(book=book).select_related('author')
        authors_list = [
            {
                "id": ba.author.id,
                "name": ba.author.name,
                "role": ba.author_role
            }
            for ba in book_authors
        ]
        
        book_data = {
            "success": True,
            "book": {
                "id": book.id,
                "book_id": book.book_id,
                "isbn": book.isbn or "",
                "title": book.title,
                "subtitle": book.subtitle or "",
                "description": book.description or "",
                "publication_date": book.publication_date.strftime('%Y-%m-%d') if book.publication_date else "",
                "edition": book.edition or "",
                "pages": book.pages or "",
                "language": book.language,
                "cover_image_url": book.cover_image_url or "",
                "category_id": book.category.id if book.category else None,
                "category_name": book.category.category_name if book.category else "N/A",
                "publisher_id": book.publisher.id if book.publisher else None,
                "publisher_name": book.publisher.publisher_name if book.publisher else "N/A",
                "quantity": book.quantity,
                "total_copies": book.total_copies,
                "availability": book.availability,
                "authors": authors_list,
                "created_at": book.created_at.strftime('%Y-%m-%d %H:%M:%S') if book.created_at else "",
                "updated_at": book.updated_at.strftime('%Y-%m-%d %H:%M:%S') if book.updated_at else "",
            }
        }
        return JsonResponse(book_data)
    
    except Book.DoesNotExist:
        return JsonResponse({"success": False, "error": "Book not found"}, status=404)
    except Exception as e:
        logger.exception("Error fetching book details: %s", e)
        return JsonResponse({"success": False, "error": str(e)}, status=500)
