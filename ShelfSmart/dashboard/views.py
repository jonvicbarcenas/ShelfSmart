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
        "branch_count": "10",
        "overdue_borrowers": ["Sasmith Gunasekara (ID: 10)", "Dulani Perera (ID: 12)"],
        "admins": ["Nisal Gunasekara (Active)", "Sithija Perera (Inactive)"],
        "branches": [
            "BookWorm - Matara (ID:1)",
            "BookWorm - Colombo (ID:2)"
        ],
    }
    return render(request, "dashboard/dashboard.html", context)
