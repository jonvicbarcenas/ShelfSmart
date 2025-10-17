from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from user_auth.decorators import user_required

# Create your views here.

@user_required
def profile_view(request):
    """
    User profile view - displays and allows editing of user profile
    """
    context = {
        'user': request.user,
    }
    return render(request, 'user_profile/profile.html', context)
