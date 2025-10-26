from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from user_auth.decorators import admin_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import logging

from admin.common.models import Publisher

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
def publisher_management(request):
    """Publisher Management - CRUD operations for publishers"""
    try:
        logger.info("[publisher_management] %s by user=%s", request.method, getattr(request, "user", None))
    except Exception:
        pass
    
    if request.method == "POST":
        action = request.POST.get("action")
        user_type = getattr(request.user, "user_type", "user")
        
        if user_type != "admin":
            messages.error(request, "You do not have permission to modify publishers.")
            return redirect("/admin-panel/publishers/")

        try:
            logger.info("[publisher_management] POST action=%s data=%s", action, dict(request.POST))
            
            if action == "add":
                # Add new publisher
                publisher_name = request.POST.get("publisher_name", "").strip()
                address = request.POST.get("address", "").strip()
                phone = request.POST.get("phone", "").strip()
                email = request.POST.get("email", "").strip()
                website = request.POST.get("website", "").strip()
                established_year = request.POST.get("established_year", "").strip()

                if not publisher_name:
                    messages.error(request, "Publisher name is required.")
                    return redirect("/admin-panel/publishers/")

                # Check if publisher name already exists
                if Publisher.objects.filter(publisher_name=publisher_name).exists():
                    messages.error(request, f"Publisher '{publisher_name}' already exists.")
                    return redirect("/admin-panel/publishers/")

                publisher = Publisher(
                    publisher_name=publisher_name,
                    address=address if address else None,
                    phone=phone if phone else None,
                    email=email if email else None,
                    website=website if website else None,
                    established_year=int(established_year) if established_year else None
                )
                publisher.save()
                logger.info("[publisher_management] Created publisher id=%s", publisher.id)
                messages.success(request, "Publisher added successfully!")

            elif action == "edit":
                # Update publisher
                publisher_id = request.POST.get("publisher_id")
                publisher = Publisher.objects.get(pk=publisher_id)
                
                new_name = request.POST.get("publisher_name", "").strip()
                new_address = request.POST.get("address", "").strip()
                new_phone = request.POST.get("phone", "").strip()
                new_email = request.POST.get("email", "").strip()
                new_website = request.POST.get("website", "").strip()
                new_year = request.POST.get("established_year", "").strip()

                if not new_name:
                    messages.error(request, "Publisher name is required.")
                    return redirect("/admin-panel/publishers/")

                # Check if new name conflicts with another publisher
                existing = Publisher.objects.filter(publisher_name=new_name).exclude(pk=publisher_id)
                if existing.exists():
                    messages.error(request, f"Publisher '{new_name}' already exists.")
                    return redirect("/admin-panel/publishers/")

                publisher.publisher_name = new_name
                publisher.address = new_address if new_address else None
                publisher.phone = new_phone if new_phone else None
                publisher.email = new_email if new_email else None
                publisher.website = new_website if new_website else None
                publisher.established_year = int(new_year) if new_year else None

                publisher.save()
                logger.info("[publisher_management] Updated publisher id=%s", publisher.id)
                messages.success(request, "Publisher updated successfully!")

            elif action == "delete":
                # Delete publisher
                publisher_id = request.POST.get("publisher_id")
                publisher = Publisher.objects.get(pk=publisher_id)
                
                # Check if publisher has books
                if publisher.books.exists():
                    messages.error(request, f"Cannot delete publisher '{publisher.publisher_name}' because it has books assigned to it.")
                    return redirect("/admin-panel/publishers/")
                
                publisher_name = publisher.publisher_name
                publisher.delete()
                logger.info("[publisher_management] Deleted publisher: %s", publisher_name)
                messages.success(request, f"Publisher '{publisher_name}' deleted successfully!")

        except Exception as e:
            logger.exception("[publisher_management] Error in mutation: %s", e)
            messages.error(request, f"Error: {str(e)}")

        return redirect("/admin-panel/publishers/")
    
    # GET request - fetch all publishers
    try:
        publishers_qs = Publisher.objects.all().order_by('publisher_name')
        publishers = []
        
        for p in publishers_qs:
            publishers.append({
                "id": p.id,
                "publisher_id": p.publisher_id,
                "publisher_name": p.publisher_name,
                "address": p.address or "",
                "phone": p.phone or "",
                "email": p.email or "",
                "website": p.website or "",
                "established_year": p.established_year or "",
                "created_at": p.created_at,
                "updated_at": p.updated_at,
                "book_count": p.books.count(),
            })

        context = {
            "user_info": get_current_user_info(request),
            "publishers": publishers,
        }
        return render(request, "publisher_management/publisher_management.html", context)
    
    except Exception as e:
        logger.exception("[publisher_management] Error loading publishers: %s", e)
        messages.error(request, f"Error loading publishers: {str(e)}")
        return render(request, "publisher_management/publisher_management.html", {
            "user_info": get_current_user_info(request),
            "publishers": [],
        })
