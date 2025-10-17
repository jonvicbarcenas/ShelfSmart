from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from user_auth.decorators import user_required

# Create your views here.

@user_required
def profile_view(request):
    """
    User profile view - displays and allows editing of user profile
    """
    user_info = {
        'full_name': f"{request.user.first_name} {request.user.last_name}",
        'role': request.user.get_user_type_display(),
        'username': request.user.username
    }
    context = {
        'user': request.user,
        'user_info': user_info,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'username': request.user.username,
        'email': request.user.email,
        'phone': request.user.phone,
        'status': 'Active' if request.user.is_active else 'Inactive',
    }
    return render(request, 'user_profile/profile.html', context)
