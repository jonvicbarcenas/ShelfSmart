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
def user_management(request):
    """User Management - CRUD operations"""
    if request.method == "POST":
        action = request.POST.get("action")
        
        try:
            if action == "add":
                # Add new user
                user_data = {
                    "name": request.POST.get("name"),
                    "email": request.POST.get("email"),
                    "username": request.POST.get("username"),
                    "role": request.POST.get("role", "student"),
                }
                supabase.table("dashboard_user").insert(user_data).execute()
                messages.success(request, "User added successfully!")
                
            elif action == "edit":
                # Update user
                user_id = request.POST.get("user_id")
                user_data = {
                    "name": request.POST.get("name"),
                    "email": request.POST.get("email"),
                    "username": request.POST.get("username"),
                }
                supabase.table("dashboard_user").update(user_data).eq("id", user_id).execute()
                messages.success(request, "User updated successfully!")
                
            elif action == "delete":
                # Delete user
                user_id = request.POST.get("user_id")
                supabase.table("dashboard_user").delete().eq("id", user_id).execute()
                messages.success(request, "User deleted successfully!")
                
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
        
        return redirect("/admin-panel/users/")
    
    # GET request - fetch all users
    try:
        users_response = supabase.table("dashboard_user").select("*").execute()
        users = users_response.data if users_response.data else []
        
        context = {
            "user_info": get_current_user_info(request),
            "users": users,
        }
        return render(request, "user_management/user_management.html", context)
    
    except Exception as e:
        messages.error(request, f"Error loading users: {str(e)}")
        return render(request, "user_management/user_management.html", {
            "user_info": get_current_user_info(request),
            "users": []
        })
