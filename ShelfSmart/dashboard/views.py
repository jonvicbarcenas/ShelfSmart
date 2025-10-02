from django.shortcuts import render

def userborrow(request):
    return render(request, 'userborrow.html')

def dashboard_view(request):
    # Simulate getting user role from DB (change this to "Admin" to test admin view)
    role = "User"

    context = {
        "user_name": "Nisal Gunasekara",
        "role": role,
        "total_users": "150",
        "total_books": "1500",
        "books_in_circulation": "045",
        "overdue_borrowers": ["Sasmith Gunasekara (ID: 10)", "Dulani Perera (ID: 12)"],
        "admins": ["Nisal Gunasekara (Active)", "Sithija Perera (Inactive)"],
    }
    return render(request, "dashboard/admin_dashboard.html", context)


def catalog_admin(request):
    return render(request, "dashboard/catalog_admin.html")

def book_management(request):
    return render(request, "dashboard/book_management.html")

def user_management(request):
    return render(request, "dashboard/user_management.html")

def admin_profile(request):
    # You can fetch actual admin data from your database here
    context = {
        "user_name": "Jascha B. Base",
        "role": "Admin",
        "email": "jascha.base@shelfsmart.edu",
        "phone": "+1 (555) 123-4567",
        "year": "2025",
        "address": "123 University Ave, Campus City"
    }
    return render(request, "dashboard/admin_profile.html", context)

def student_profile(request):
    # You can fetch actual student data from your database here
    context = {
        "user_name": "Nisal Gunasekara",
        "student_id": "STU-2024-001",
        "role": "Student",
        "email": "nisal.gunasekara@bookworm.edu",
        "phone": "+1 (555) 123-4567",
        "course": "Computer Science",
        "year": "3rd Year",
        "address": "123 University Ave, Campus City"
    }
    return render(request, "dashboard/student_profile.html", context)



def userborrow(request):
    return render(request, "dashboard/user_borrow.html")