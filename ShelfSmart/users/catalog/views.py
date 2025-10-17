from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from user_auth.decorators import user_required

# Create your views here.

@user_required
def catalog_view(request):
    """
    User catalog view - displays available books for borrowing
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
    return render(request, 'catalog/catalog.html', context)
