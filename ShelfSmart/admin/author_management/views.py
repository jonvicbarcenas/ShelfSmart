from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from user_auth.decorators import admin_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import logging

from admin.common.models import Author

logger = logging.getLogger(__name__)


def get_current_user_info(request):
    """Helper function to get current user's info from Django User object"""
    if request.user.is_authenticated:
        user = request.user
        first_name = user.first_name or "User"
        last_name = user.last_name or ""
        full_name = f"{first_name} {last_name}".strip() if last_name else first_name
        username = user.username or "username"
        role = getattr(user, 'user_type', 'user').capitalize()
        
        return {
            "full_name": full_name,
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "role": role
        }
    
    return {
        "full_name": "User",
        "first_name": "User",
        "last_name": "",
        "username": "username",
        "role": "User"
    }


@admin_required
def author_management(request):
    """Author Management - CRUD operations for authors"""
    try:
        logger.info("[author_management] %s by user=%s", request.method, getattr(request, "user", None))
    except Exception:
        pass
    
    if request.method == "POST":
        action = request.POST.get("action")
        user_type = getattr(request.user, "user_type", "user")
        
        if user_type != "admin":
            messages.error(request, "You do not have permission to modify authors.")
            return redirect("/admin-panel/authors/")

        try:
            logger.info("[author_management] POST action=%s data=%s", action, dict(request.POST))
            
            if action == "add":
                # Add new author
                name = request.POST.get("name", "").strip()
                biography = request.POST.get("biography", "").strip()
                nationality = request.POST.get("nationality", "").strip()

                if not name:
                    messages.error(request, "Author name is required.")
                    return redirect("/admin-panel/authors/")

                # Check if author name already exists
                if Author.objects.filter(name=name).exists():
                    messages.error(request, f"Author '{name}' already exists.")
                    return redirect("/admin-panel/authors/")

                author = Author(
                    name=name,
                    biography=biography if biography else None,
                    nationality=nationality if nationality else None
                )
                author.save()
                logger.info("[author_management] Created author id=%s", author.id)
                messages.success(request, "Author added successfully!")

            elif action == "edit":
                # Update author
                author_id = request.POST.get("author_id")
                author = Author.objects.get(pk=author_id)
                
                new_name = request.POST.get("name", "").strip()
                new_biography = request.POST.get("biography", "").strip()
                new_nationality = request.POST.get("nationality", "").strip()

                if not new_name:
                    messages.error(request, "Author name is required.")
                    return redirect("/admin-panel/authors/")

                # Check if new name conflicts with another author
                existing = Author.objects.filter(name=new_name).exclude(pk=author_id)
                if existing.exists():
                    messages.error(request, f"Author '{new_name}' already exists.")
                    return redirect("/admin-panel/authors/")

                author.name = new_name
                author.biography = new_biography if new_biography else None
                author.nationality = new_nationality if new_nationality else None

                author.save()
                logger.info("[author_management] Updated author id=%s", author.id)
                messages.success(request, "Author updated successfully!")

            elif action == "delete":
                # Delete author
                author_id = request.POST.get("author_id")
                author = Author.objects.get(pk=author_id)
                
                # Check if author has books
                if author.book_authors.exists():
                    messages.error(request, f"Cannot delete author '{author.name}' because they have books assigned to them.")
                    return redirect("/admin-panel/authors/")
                
                author_name = author.name
                author.delete()
                logger.info("[author_management] Deleted author: %s", author_name)
                messages.success(request, f"Author '{author_name}' deleted successfully!")

        except Exception as e:
            logger.exception("[author_management] Error in mutation: %s", e)
            messages.error(request, f"Error: {str(e)}")

        return redirect("/admin-panel/authors/")
    
    # GET request - fetch all authors
    try:
        authors_qs = Author.objects.all().order_by('name')
        authors = []
        
        for a in authors_qs:
            authors.append({
                "id": a.id,
                "author_id": a.author_id,
                "name": a.name,
                "biography": a.biography or "",
                "nationality": a.nationality or "",
                "created_at": a.created_at,
                "updated_at": a.updated_at,
                "book_count": a.book_authors.count(),
            })

        context = {
            "user_info": get_current_user_info(request),
            "authors": authors,
            "active_page": "authors",
        }
        return render(request, "author_management/author_management.html", context)
    
    except Exception as e:
        logger.exception("[author_management] Error loading authors: %s", e)
        messages.error(request, f"Error loading authors: {str(e)}")
        return render(request, "author_management/author_management.html", {
            "user_info": get_current_user_info(request),
            "authors": [],
            "active_page": "authors",
        })
