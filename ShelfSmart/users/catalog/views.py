from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from user_auth.decorators import user_required

# Create your views here.

@user_required
def catalog_view(request):
    """
    User catalog view - displays available books for borrowing
    """
    context = {
        'user': request.user,
    }
    return render(request, 'catalog/catalog.html', context)
