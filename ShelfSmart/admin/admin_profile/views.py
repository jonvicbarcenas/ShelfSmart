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
def admin_profile(request):
    """Admin Profile with UPDATE functionality"""
    # Get admin ID from session (you should implement proper authentication)
    admin_id = request.session.get('user_id', 1)  # Default to 1 for testing
    
    if request.method == "POST":
        try:
            # Update admin profile
            profile_data = {
                "name": request.POST.get("fullName"),
                "email": request.POST.get("email"),
                "phone": request.POST.get("phone"),
                "address": request.POST.get("address"),
                "year": request.POST.get("year"),
            }
            
            supabase.table("dashboard_user").update(profile_data).eq("id", admin_id).execute()
            messages.success(request, "Profile updated successfully!")
            
            # Fetch updated data
            admin_response = supabase.table("dashboard_user").select("*").eq("id", admin_id).execute()
            admin_data = admin_response.data[0] if admin_response.data else {}
            
        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")
            admin_data = {}
        
        return redirect("/admin-panel/profile/")
    
    # GET request - fetch admin data
    try:
        admin_response = supabase.table("dashboard_user")\
            .select("*")\
            .eq("id", admin_id)\
            .eq("role", "admin")\
            .execute()
        
        if admin_response.data:
            admin_data = admin_response.data[0]
            context = {
                "user_info": get_current_user_info(request),
                "user_name": admin_data.get("name", "Admin User"),
                "role": "Admin",
                "email": admin_data.get("email", ""),
                "phone": admin_data.get("phone", ""),
                "year": admin_data.get("year", "2025"),
                "address": admin_data.get("address", ""),
                "user_id": admin_id,
            }
        else:
            context = {
                "user_info": get_current_user_info(request),
                "user_name": "Admin User",
                "role": "Admin",
                "email": "",
                "phone": "",
                "year": "2025",
                "address": "",
                "user_id": admin_id,
            }
        
        return render(request, "admin_profile/admin_profile.html", context)
    
    except Exception as e:
        messages.error(request, f"Error loading profile: {str(e)}")
        return render(request, "admin_profile/admin_profile.html", {
            "user_info": get_current_user_info(request),
            "user_name": "Admin User",
            "role": "Admin",
            "email": "",
            "phone": "",
            "year": "2025",
            "address": "",
        })
