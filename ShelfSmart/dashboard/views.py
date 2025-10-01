from django.shortcuts import render

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
