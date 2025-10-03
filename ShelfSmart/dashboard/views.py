from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime, date
from .supabase_client import supabase
import json

def dashboard_view(request):
    """Admin Dashboard with real-time data from Supabase"""
    try:
        # Fetch total users
        users_response = supabase.table("users").select("*").execute()
        total_users = len(users_response.data) if users_response.data else 0

        # Fetch total books
        books_response = supabase.table("books").select("*").execute()
        total_books = len(books_response.data) if books_response.data else 0

        # Fetch overdue borrowers
        today = date.today().isoformat()
        overdue_response = supabase.table("borrow_records")\
            .select("*, users(name, id), books(title)")\
            .lt("due_date", today)\
            .eq("is_returned", False)\
            .execute()
        
        # Fetch borrowed books stats for chart
        borrowed_response = supabase.table("borrow_records")\
            .select("*")\
            .eq("is_returned", False)\
            .execute()
        
        returned_response = supabase.table("borrow_records")\
            .select("*")\
            .eq("is_returned", True)\
            .execute()
        
        # Fetch active admins
        admins_response = supabase.table("users")\
            .select("*")\
            .eq("role", "admin")\
            .execute()

        context = {
            "total_users": total_users,
            "total_books": total_books,
            "overdue_borrowers": overdue_response.data if overdue_response.data else [],
            "total_borrowed": len(borrowed_response.data) if borrowed_response.data else 0,
            "total_returned": len(returned_response.data) if returned_response.data else 0,
            "admins": admins_response.data if admins_response.data else [],
        }

        return render(request, "dashboard/admin_dashboard.html", context)
    
    except Exception as e:
        messages.error(request, f"Error loading dashboard: {str(e)}")
        return render(request, "dashboard/admin_dashboard.html", {
            "total_users": 0,
            "total_books": 0,
            "overdue_borrowers": [],
            "total_borrowed": 0,
            "total_returned": 0,
            "admins": [],
        })


def catalog_admin(request):
    """Catalog management - Borrowed and Overdue books"""
    try:
        # Fetch borrowed books
        borrowed_books = supabase.table("borrow_records")\
            .select("*, users(name, id), books(title, id)")\
            .eq("is_returned", False)\
            .execute()

        # Fetch overdue books
        today = date.today().isoformat()
        overdue_books = supabase.table("borrow_records")\
            .select("*, users(name, id), books(title, id)")\
            .lt("due_date", today)\
            .eq("is_returned", False)\
            .execute()

        context = {
            "borrowed_books": borrowed_books.data if borrowed_books.data else [],
            "overdue_books": overdue_books.data if overdue_books.data else [],
        }

        return render(request, "dashboard/catalog_admin.html", context)
    
    except Exception as e:
        messages.error(request, f"Error loading catalog: {str(e)}")
        return render(request, "dashboard/catalog_admin.html", {
            "borrowed_books": [],
            "overdue_books": [],
        })


def book_management(request):
    """Book Management - CRUD operations"""
    if request.method == "POST":
        action = request.POST.get("action")
        
        try:
            if action == "add":
                # Add new book
                book_data = {
                    "title": request.POST.get("name"),
                    "type": request.POST.get("type"),
                    "language": request.POST.get("language"),
                    "author": request.POST.get("author", "Unknown"),
                    "total_copies": int(request.POST.get("total_copies", 1)),
                    "available_copies": int(request.POST.get("available_copies", 1)),
                }
                supabase.table("books").insert(book_data).execute()
                messages.success(request, "Book added successfully!")
                
            elif action == "edit":
                # Update book
                book_id = request.POST.get("book_id")
                book_data = {
                    "title": request.POST.get("name"),
                    "type": request.POST.get("type"),
                    "language": request.POST.get("language"),
                    "total_copies": int(request.POST.get("total_copies", 1)),
                    "available_copies": int(request.POST.get("available_copies", 1)),
                }
                supabase.table("books").update(book_data).eq("id", book_id).execute()
                messages.success(request, "Book updated successfully!")
                
            elif action == "delete":
                # Delete book
                book_id = request.POST.get("book_id")
                supabase.table("books").delete().eq("id", book_id).execute()
                messages.success(request, "Book deleted successfully!")
                
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
        
        return redirect("book_management")
    
    # GET request - fetch all books
    try:
        books_response = supabase.table("books").select("*").execute()
        books = books_response.data if books_response.data else []
        
        # Add computed availability status for display
        for book in books:
            book['availability'] = 'Available' if book.get('available_copies', 0) > 0 else 'Borrowed'
        
        context = {
            "books": books,
        }
        return render(request, "dashboard/book_management.html", context)
    
    except Exception as e:
        messages.error(request, f"Error loading books: {str(e)}")
        return render(request, "dashboard/book_management.html", {"books": []})


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
                supabase.table("users").insert(user_data).execute()
                messages.success(request, "User added successfully!")
                
            elif action == "edit":
                # Update user
                user_id = request.POST.get("user_id")
                user_data = {
                    "name": request.POST.get("name"),
                    "email": request.POST.get("email"),
                    "username": request.POST.get("username"),
                }
                supabase.table("users").update(user_data).eq("id", user_id).execute()
                messages.success(request, "User updated successfully!")
                
            elif action == "delete":
                # Delete user
                user_id = request.POST.get("user_id")
                supabase.table("users").delete().eq("id", user_id).execute()
                messages.success(request, "User deleted successfully!")
                
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
        
        return redirect("user_management")
    
    # GET request - fetch all users
    try:
        users_response = supabase.table("users").select("*").execute()
        users = users_response.data if users_response.data else []
        
        context = {
            "users": users,
        }
        return render(request, "dashboard/user_management.html", context)
    
    except Exception as e:
        messages.error(request, f"Error loading users: {str(e)}")
        return render(request, "dashboard/user_management.html", {"users": []})


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
            
            supabase.table("users").update(profile_data).eq("id", admin_id).execute()
            messages.success(request, "Profile updated successfully!")
            
            # Fetch updated data
            admin_response = supabase.table("users").select("*").eq("id", admin_id).execute()
            admin_data = admin_response.data[0] if admin_response.data else {}
            
        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")
            admin_data = {}
        
        return redirect("admin_profile")
    
    # GET request - fetch admin data
    try:
        admin_response = supabase.table("users")\
            .select("*")\
            .eq("id", admin_id)\
            .eq("role", "admin")\
            .execute()
        
        if admin_response.data:
            admin_data = admin_response.data[0]
            context = {
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
                "user_name": "Admin User",
                "role": "Admin",
                "email": "",
                "phone": "",
                "year": "2025",
                "address": "",
                "user_id": admin_id,
            }
        
        return render(request, "dashboard/admin_profile.html", context)
    
    except Exception as e:
        messages.error(request, f"Error loading profile: {str(e)}")
        return render(request, "dashboard/admin_profile.html", {
            "user_name": "Admin User",
            "role": "Admin",
            "email": "",
            "phone": "",
            "year": "2025",
            "address": "",
        })


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
            
            supabase.table("users").update(profile_data).eq("id", student_id).execute()
            messages.success(request, "Profile updated successfully!")
            
        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")
        
        return redirect("student_profile")
    
    # GET request - fetch student data
    try:
        student_response = supabase.table("users")\
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
        
        return render(request, "dashboard/student_profile.html", context)
    
    except Exception as e:
        messages.error(request, f"Error loading profile: {str(e)}")
        return render(request, "dashboard/student_profile.html", {
            "user_name": "Student",
            "student_id": "STU-001",
            "role": "Student",
            "email": "",
            "phone": "",
            "course": "",
            "year": "",
            "address": "",
        })

def userborrow(request):
    # Example placeholder code
    return render(request, "dashboard/userborrow.html", {})