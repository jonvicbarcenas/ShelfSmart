from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from user_auth.decorators import user_required

# Create your views here.

@user_required
def dashboard_view(request):
    """
    User dashboard view - displays user's borrowed books, notifications, etc.
    """
    user_info = {
        'full_name': f"{request.user.first_name} {request.user.last_name}",
        'role': request.user.get_user_type_display(),
        'username': request.user.username
    }
    context = {
        'user': request.user,
        'user_info': user_info,
    }
    return render(request, 'user_dashboard/dashboard.html', context)
