from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def profile_view(request):
    """
    User profile view - displays and allows editing of user profile
    """
    context = {
        'user': request.user,
    }
    return render(request, 'user_profile/profile.html', context)
