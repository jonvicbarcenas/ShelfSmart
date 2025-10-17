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
def student_profile(request):
    """Student Profile with UPDATE functionality"""
    # Get student ID from session
    student_id = request.session.get('user_id', 1)  # Default to 1 for testing
    
    if request.method == "POST":
        try:
            # Update student profile
            profile_data = {
                "name": request.POST.get("fullName"),
                "email": request.POST.get("email"),
                "phone": request.POST.get("phone"),
                "address": request.POST.get("address"),
                "course": request.POST.get("course"),
                "year": request.POST.get("year"),
            }
            
            supabase.table("dashboard_user").update(profile_data).eq("id", student_id).execute()
            messages.success(request, "Profile updated successfully!")
            
        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")
        
        return redirect("/admin-panel/student/")
    
    # GET request - fetch student data
    try:
        student_response = supabase.table("dashboard_user")\
            .select("*")\
            .eq("id", student_id)\
            .eq("role", "student")\
            .execute()
        
        if student_response.data:
            student_data = student_response.data[0]
            context = {
                "user_name": student_data.get("name", "Student"),
                "student_id": f"STU-{student_data.get('id', '001')}",
                "role": "Student",
                "email": student_data.get("email", ""),
                "phone": student_data.get("phone", ""),
                "course": student_data.get("course", ""),
                "year": student_data.get("year", ""),
                "address": student_data.get("address", ""),
                "user_id": student_id,
            }
        else:
            context = {
                "user_name": "Student",
                "student_id": "STU-001",
                "role": "Student",
                "email": "",
                "phone": "",
                "course": "",
                "year": "",
                "address": "",
            }
        
        return render(request, "student_catalog/student_profile.html", context)
    
    except Exception as e:
        messages.error(request, f"Error loading profile: {str(e)}")
        return render(request, "student_catalog/student_profile.html", {
            "user_name": "Student",
            "student_id": "STU-001",
            "role": "Student",
            "email": "",
            "phone": "",
            "course": "",
            "year": "",
            "address": "",
        })
