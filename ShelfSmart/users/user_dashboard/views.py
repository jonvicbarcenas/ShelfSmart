from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from user_auth.decorators import user_required

# Create your views here.

@user_required
def dashboard_view(request):
    """
    User dashboard view - displays user's borrowed books, notifications, etc.
    """
    context = {
        'user': request.user,
    }
    return render(request, 'user_dashboard/dashboard.html', context)
