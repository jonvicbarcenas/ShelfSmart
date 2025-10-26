from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from user_auth.decorators import admin_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import logging

from admin.common.models import Category

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
def category_management(request):
    """Category Management - CRUD operations for categories"""
    try:
        logger.info("[category_management] %s by user=%s", request.method, getattr(request, "user", None))
    except Exception:
        pass
    
    if request.method == "POST":
        action = request.POST.get("action")
        user_type = getattr(request.user, "user_type", "user")
        
        if user_type != "admin":
            messages.error(request, "You do not have permission to modify categories.")
            return redirect("/admin-panel/categories/")

        try:
            logger.info("[category_management] POST action=%s data=%s", action, dict(request.POST))
            
            if action == "add":
                # Add new category
                category_name = request.POST.get("category_name", "").strip()
                description = request.POST.get("description", "").strip()
                parent_category_id = request.POST.get("parent_category_id")

                if not category_name:
                    messages.error(request, "Category name is required.")
                    return redirect("/admin-panel/categories/")

                # Check if category name already exists
                if Category.objects.filter(category_name=category_name).exists():
                    messages.error(request, f"Category '{category_name}' already exists.")
                    return redirect("/admin-panel/categories/")

                parent_category = None
                if parent_category_id:
                    try:
                        parent_category = Category.objects.get(pk=parent_category_id)
                    except Category.DoesNotExist:
                        messages.error(request, "Invalid parent category selected.")
                        return redirect("/admin-panel/categories/")

                category = Category(
                    category_name=category_name,
                    description=description if description else None,
                    parent_category=parent_category
                )
                category.save()
                logger.info("[category_management] Created category id=%s", category.id)
                messages.success(request, "Category added successfully!")

            elif action == "edit":
                # Update category
                category_id = request.POST.get("category_id")
                category = Category.objects.get(pk=category_id)
                
                new_name = request.POST.get("category_name", "").strip()
                new_description = request.POST.get("description", "").strip()
                new_parent_id = request.POST.get("parent_category_id")

                if not new_name:
                    messages.error(request, "Category name is required.")
                    return redirect("/admin-panel/categories/")

                # Check if new name conflicts with another category
                existing = Category.objects.filter(category_name=new_name).exclude(pk=category_id)
                if existing.exists():
                    messages.error(request, f"Category '{new_name}' already exists.")
                    return redirect("/admin-panel/categories/")

                category.category_name = new_name
                category.description = new_description if new_description else None
                
                # Handle parent category
                if new_parent_id:
                    if int(new_parent_id) == int(category_id):
                        messages.error(request, "A category cannot be its own parent.")
                        return redirect("/admin-panel/categories/")
                    try:
                        category.parent_category = Category.objects.get(pk=new_parent_id)
                    except Category.DoesNotExist:
                        messages.error(request, "Invalid parent category selected.")
                        return redirect("/admin-panel/categories/")
                else:
                    category.parent_category = None

                category.save()
                logger.info("[category_management] Updated category id=%s", category.id)
                messages.success(request, "Category updated successfully!")

            elif action == "delete":
                # Delete category
                category_id = request.POST.get("category_id")
                category = Category.objects.get(pk=category_id)
                
                # Check if category has books
                if category.books.exists():
                    messages.error(request, f"Cannot delete category '{category.category_name}' because it has books assigned to it.")
                    return redirect("/admin-panel/categories/")
                
                # Check if category has subcategories
                if category.subcategories.exists():
                    messages.error(request, f"Cannot delete category '{category.category_name}' because it has subcategories.")
                    return redirect("/admin-panel/categories/")
                
                category_name = category.category_name
                category.delete()
                logger.info("[category_management] Deleted category: %s", category_name)
                messages.success(request, f"Category '{category_name}' deleted successfully!")

        except Exception as e:
            logger.exception("[category_management] Error in mutation: %s", e)
            messages.error(request, f"Error: {str(e)}")

        return redirect("/admin-panel/categories/")
    
    # GET request - fetch all categories
    try:
        categories_qs = Category.objects.select_related('parent_category').all().order_by('category_name')
        categories = []
        
        for c in categories_qs:
            categories.append({
                "id": c.id,
                "category_id": c.category_id,
                "category_name": c.category_name,
                "description": c.description or "",
                "parent_category_id": c.parent_category.id if c.parent_category else None,
                "parent_category_name": c.parent_category.category_name if c.parent_category else None,
                "full_path": c.get_full_path(),
                "created_at": c.created_at,
                "updated_at": c.updated_at,
                "book_count": c.books.count(),
                "subcategory_count": c.subcategories.count(),
            })

        # Get root categories for parent dropdown
        root_categories = Category.objects.filter(parent_category__isnull=True).order_by('category_name')

        context = {
            "user_info": get_current_user_info(request),
            "categories": categories,
            "root_categories": root_categories,
        }
        return render(request, "category_management/category_management.html", context)
    
    except Exception as e:
        logger.exception("[category_management] Error loading categories: %s", e)
        messages.error(request, f"Error loading categories: {str(e)}")
        return render(request, "category_management/category_management.html", {
            "user_info": get_current_user_info(request),
            "categories": [],
            "root_categories": [],
        })
