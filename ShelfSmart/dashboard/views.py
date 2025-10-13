from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from datetime import datetime, date
from .supabase_client import supabase
import json

def get_current_user_info(request):
    """Helper function to get current user's info from Django User object"""
    # Use Django's authenticated user instead of querying Supabase
    if request.user.is_authenticated:
        user = request.user
        
        # Get names from Django User model
        first_name = user.first_name or "User"
        last_name = user.last_name or ""
        full_name = f"{first_name} {last_name}".strip() if last_name else first_name
        username = user.username or "username"
        
        # Determine role from user properties
        if user.is_superuser:
            role = "Admin"
        elif hasattr(user, 'is_staff') and user.is_staff:
            role = "Admin"
        else:
            role = "User"
        
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
def dashboard_view(request):
    """Admin Dashboard with real-time data from Supabase"""
    try:
        # Fetch total users
        users_response = supabase.table("dashboard_user").select("*").execute()
        total_users = len(users_response.data) if users_response.data else 0

        # Fetch total books
        books_response = supabase.table("dashboard_book").select("*").execute()
        total_books = len(books_response.data) if books_response.data else 0

        # Fetch overdue borrowers
        today = date.today().isoformat()
        overdue_response = supabase.table("dashboard_borrowrecord")\
            .select("*, users:dashboard_user(name, id), books:dashboard_book(title)")\
            .lt("due_date", today)\
            .eq("is_returned", False)\
            .execute()
        
        # Fetch borrowed books stats for chart
        borrowed_response = supabase.table("dashboard_borrowrecord")\
            .select("*")\
            .eq("is_returned", False)\
            .execute()
        
        returned_response = supabase.table("dashboard_borrowrecord")\
            .select("*")\
            .eq("is_returned", True)\
            .execute()
        
        # Fetch active admins
        admins_response = supabase.table("dashboard_user")\
            .select("*")\
            .eq("role", "admin")\
            .execute()

        context = {
            "user_info": get_current_user_info(request),
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
            "user_info": get_current_user_info(request),
            "total_users": 0,
            "total_books": 0,
            "overdue_borrowers": [],
            "total_borrowed": 0,
            "total_returned": 0,
            "admins": [],
        })


@login_required
def catalog_admin(request):
    """Catalog management - Borrowed and Overdue books"""
    if request.method == "POST":
        action = request.POST.get("action")
        
        try:
            if action == "return":
                # Mark book as returned
                borrow_id = request.POST.get("borrow_id")
                from datetime import date
                
                # Update borrow record
                supabase.table("dashboard_borrowrecord").update({
                    "is_returned": True,
                    "return_date": date.today().isoformat()
                }).eq("id", borrow_id).execute()
                
                # Get the book_id to update availability
                borrow_record = supabase.table("dashboard_borrowrecord")\
                    .select("book_id")\
                    .eq("id", borrow_id)\
                    .execute()
                
                if borrow_record.data:
                    book_id = borrow_record.data[0]['book_id']
                    
                    # Update book availability
                    book = supabase.table("dashboard_book").select("available_copies").eq("id", book_id).execute()
                    if book.data:
                        new_available = book.data[0]['available_copies'] + 1
                        supabase.table("dashboard_book").update({
                            "available_copies": new_available,
                            "availability": "Available"
                        }).eq("id", book_id).execute()
                
                messages.success(request, "Book marked as returned successfully!")
                
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
        
        return redirect("catalog_admin")
    
    try:
        # Fetch borrowed books
        borrowed_books = supabase.table("dashboard_borrowrecord")\
            .select("*, users:dashboard_user(name, id), books:dashboard_book(title, id)")\
            .eq("is_returned", False)\
            .execute()

        # Fetch overdue books with days overdue calculation
        today = date.today().isoformat()
        overdue_books = supabase.table("dashboard_borrowrecord")\
            .select("*, users:dashboard_user(name, id), books:dashboard_book(title, id)")\
            .lt("due_date", today)\
            .eq("is_returned", False)\
            .execute()
        
        # Calculate days overdue for each record
        from datetime import datetime
        for record in overdue_books.data if overdue_books.data else []:
            due_date = datetime.fromisoformat(record['due_date'])
            days_overdue = (datetime.now() - due_date).days
            record['days_overdue'] = days_overdue

        context = {
            "user_info": get_current_user_info(request),
            "borrowed_books": borrowed_books.data if borrowed_books.data else [],
            "overdue_books": overdue_books.data if overdue_books.data else [],
        }

        return render(request, "dashboard/catalog_admin.html", context)
    
    except Exception as e:
        messages.error(request, f"Error loading catalog: {str(e)}")
        return render(request, "dashboard/catalog_admin.html", {
            "user_info": get_current_user_info(request),
            "borrowed_books": [],
            "overdue_books": [],
        })


@login_required
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
                supabase.table("dashboard_book").insert(book_data).execute()
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
                supabase.table("dashboard_book").update(book_data).eq("id", book_id).execute()
                messages.success(request, "Book updated successfully!")
                
            elif action == "delete":
                # Delete book
                book_id = request.POST.get("book_id")
                supabase.table("dashboard_book").delete().eq("id", book_id).execute()
                messages.success(request, "Book deleted successfully!")
                
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
        
        return redirect("book_management")
    
    # GET request - fetch all books
    try:
        books_response = supabase.table("dashboard_book").select("*").execute()
        books = books_response.data if books_response.data else []
        
        # Add computed availability status for display
        for book in books:
            book['availability'] = 'Available' if book.get('available_copies', 0) > 0 else 'Borrowed'
        
        context = {
            "user_info": get_current_user_info(request),
            "books": books,
        }
        return render(request, "dashboard/book_management.html", context)
    
    except Exception as e:
        messages.error(request, f"Error loading books: {str(e)}")
        return render(request, "dashboard/book_management.html", {
            "user_info": get_current_user_info(request),
            "books": []
        })


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
        
        return redirect("user_management")
    
    # GET request - fetch all users
    try:
        users_response = supabase.table("dashboard_user").select("*").execute()
        users = users_response.data if users_response.data else []
        
        context = {
            "user_info": get_current_user_info(request),
            "users": users,
        }
        return render(request, "dashboard/user_management.html", context)
    
    except Exception as e:
        messages.error(request, f"Error loading users: {str(e)}")
        return render(request, "dashboard/user_management.html", {
            "user_info": get_current_user_info(request),
            "users": []
        })


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
        
        return redirect("admin_profile")
    
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
        
        return render(request, "dashboard/admin_profile.html", context)
    
    except Exception as e:
        messages.error(request, f"Error loading profile: {str(e)}")
        return render(request, "dashboard/admin_profile.html", {
            "user_info": get_current_user_info(request),
            "user_name": "Admin User",
            "role": "Admin",
            "email": "",
            "phone": "",
            "year": "2025",
            "address": "",
        })


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
        
        return redirect("student_profile")
    
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


@login_required
def userborrow(request):
    """User borrow records"""
    return render(request, "dashboard/userborrow.html")


@login_required
def student_catalog(request):
    """Student Catalog - View borrowed and returned books"""
    # Get student ID from session
    student_id = request.session.get('user_id', 1)
    
    if request.method == "POST":
        action = request.POST.get("action")
        
        try:
            if action == "return":
                # Mark book as returned
                borrow_id = request.POST.get("book_id")
                
                # Update borrow record
                supabase.table("dashboard_borrowrecord").update({
                    "is_returned": True,
                    "return_date": date.today().isoformat()
                }).eq("id", borrow_id).eq("user_id", student_id).execute()
                
                # Get the book_id to update availability
                borrow_record = supabase.table("dashboard_borrowrecord")\
                    .select("book_id")\
                    .eq("id", borrow_id)\
                    .execute()
                
                if borrow_record.data:
                    book_id = borrow_record.data[0]['book_id']
                    
                    # Update book availability
                    book = supabase.table("dashboard_book").select("available_copies").eq("id", book_id).execute()
                    if book.data:
                        new_available = book.data[0]['available_copies'] + 1
                        supabase.table("dashboard_book").update({
                            "available_copies": new_available,
                            "availability": "Available"
                        }).eq("id", book_id).execute()
                
                messages.success(request, "Book returned successfully!")
                
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
        
        return redirect("student_catalog")
    
    # GET request - fetch student's borrowed and returned books
    try:
        # Fetch borrowed books for this student - FIXED VERSION
        borrowed_books = supabase.table("dashboard_borrowrecord")\
            .select("*, books:dashboard_book(title, id)")\
            .eq("user_id", student_id)\
            .eq("is_returned", False)\
            .execute()
        
        # Fetch returned books for this student - FIXED VERSION
        returned_books = supabase.table("dashboard_borrowrecord")\
            .select("*, books:dashboard_book(title, id)")\
            .eq("user_id", student_id)\
            .eq("is_returned", True)\
            .execute()
        
        # Get student name
        student = supabase.table("dashboard_user").select("name").eq("id", student_id).execute()
        student_name = student.data[0].get("name", "Student") if student.data else "Student"
        
        context = {
            "user_name": student_name,
            "borrowed_books": borrowed_books.data if borrowed_books.data else [],
            "returned_books": returned_books.data if returned_books.data else [],
        }
        
        return render(request, "dashboard/catalog_student.html", context)
    
    except Exception as e:
        messages.error(request, f"Error loading catalog: {str(e)}")
        return render(request, "dashboard/catalog_student.html", {
            "user_name": "Student",
            "borrowed_books": [],
            "returned_books": [],
        })


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from dashboard.models import BorrowRecord  # Import your model
from django.utils import timezone

@login_required
def student_dashboard(request):
    """Student dashboard view"""
    # Get student ID from session
    student_id = request.session.get('user_id', 1)
    
    try:
        # Get student name
        student = supabase.table("dashboard_user").select("name").eq("id", student_id).execute()
        student_name = student.data[0].get("name", "Student") if student.data else "Student"
        
        # Count borrowed books (not returned)
        borrowed_response = supabase.table("dashboard_borrowrecord")\
            .select("*")\
            .eq("user_id", student_id)\
            .eq("is_returned", False)\
            .execute()
        total_borrowed = len(borrowed_response.data) if borrowed_response.data else 0
        
        # Count returned books
        returned_response = supabase.table("dashboard_borrowrecord")\
            .select("*")\
            .eq("user_id", student_id)\
            .eq("is_returned", True)\
            .execute()
        total_returned = len(returned_response.data) if returned_response.data else 0
        
        # Count overdue books
        today = date.today().isoformat()
        overdue_response = supabase.table("dashboard_borrowrecord")\
            .select("*")\
            .eq("user_id", student_id)\
            .lt("due_date", today)\
            .eq("is_returned", False)\
            .execute()
        total_overdue = len(overdue_response.data) if overdue_response.data else 0
        
        # Get recent activities (last 5 borrow records)
        recent_response = supabase.table("dashboard_borrowrecord")\
            .select("*, books:dashboard_book(title, id)")\
            .eq("user_id", student_id)\
            .order("borrowed_date", desc=True)\
            .limit(5)\
            .execute()
        
        recent_activities = []
        if recent_response.data:
            from datetime import datetime
            for record in recent_response.data:
                if record.get('is_returned'):
                    status = 'returned'
                elif record.get('due_date') and record['due_date'] < today:
                    status = 'overdue'
                else:
                    status = 'active'
                
                recent_activities.append({
                    'books': {'title': record.get('books', {}).get('title', 'Unknown Book')},
                    'borrowed_date': record.get('borrowed_date'),
                    'status': status
                })
        
        context = {
            'user_name': student_name,
            'total_borrowed': total_borrowed,
            'total_returned': total_returned,
            'total_overdue': total_overdue,
            'recent_activities': recent_activities,
        }
        
        return render(request, 'dashboard/student_dashboard.html', context)
        
    except Exception as e:
        # Handle any errors gracefully
        messages.error(request, f"Error loading dashboard: {str(e)}")
        context = {
            'user_name': 'Student',
            'total_borrowed': 0,
            'total_returned': 0,
            'total_overdue': 0,
            'recent_activities': [],
        }
        return render(request, 'dashboard/student_dashboard.html', context)
