from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def catalog_view(request):
    """
    User catalog view - displays available books for borrowing
    """
    context = {
        'user': request.user,
    }
    return render(request, 'catalog/catalog.html', context)
