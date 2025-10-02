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