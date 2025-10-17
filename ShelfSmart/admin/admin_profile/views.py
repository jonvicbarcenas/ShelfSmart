from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from user_auth.decorators import admin_required
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import logging

from datetime import datetime, date
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
        
        # Get role directly from Django User model (user_type field)
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
def admin_profile(request):
    """Admin Profile with UPDATE functionality using Django User model"""
    # Get the current authenticated user
    user = request.user
    
    # Ensure user is an admin
    if not user.is_authenticated or user.user_type != 'admin':
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect("/admin-panel/dashboard/")
    
    if request.method == "POST":
        try:
            # Get form data
            first_name = request.POST.get("firstName", "").strip()
            last_name = request.POST.get("lastName", "").strip()
            email = request.POST.get("email", "").strip()
            phone = request.POST.get("phone", "").strip()
            username = request.POST.get("username", "").strip()
            
            # Validation
            errors = []
            
            if not first_name:
                errors.append("First name is required.")
            if not last_name:
                errors.append("Last name is required.")
            if not email:
                errors.append("Email is required.")
            else:
                try:
                    validate_email(email)
                except ValidationError:
                    errors.append("Please enter a valid email address.")
            
            if not username:
                errors.append("Username is required.")
            else:
                # Check if username is taken by another user
                if User.objects.filter(username=username).exclude(id=user.id).exists():
                    errors.append("Username is already taken.")
            
            # Check if email is taken by another user
            if email and User.objects.filter(email=email).exclude(id=user.id).exists():
                errors.append("Email is already taken.")
            
            if errors:
                for error in errors:
                    messages.error(request, error)
                return redirect("/admin-panel/profile/")
            
            # Update user profile
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.phone = phone or None
            user.username = username
            user.save()
            
            messages.success(request, "Profile updated successfully!")
            logger.info(f"Admin profile updated for user {user.username} (ID: {user.id})")
            
        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")
            logger.error(f"Error updating admin profile for user {user.id}: {str(e)}")
        
        return redirect("/admin-panel/profile/")
    
    # GET request - display profile form
    try:
        context = {
            "user_info": get_current_user_info(request),
            "user_name": user.get_full_name() or user.username,
            "role": "Admin",
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone or "",
            "username": user.username,
            "user_id": user.id,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "status": user.status,
        }
        
        return render(request, "admin_profile/admin_profile.html", context)
    
    except Exception as e:
        messages.error(request, f"Error loading profile: {str(e)}")
        logger.error(f"Error loading admin profile for user {user.id}: {str(e)}")
        return render(request, "admin_profile/admin_profile.html", {
            "user_info": get_current_user_info(request),
            "user_name": "Admin User",
            "role": "Admin",
            "first_name": "",
            "last_name": "",
            "email": "",
            "phone": "",
            "username": "",
        })
