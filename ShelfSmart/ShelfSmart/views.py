from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import json

def signup_view(request):
    if request.method == 'POST':
        try:
            # Parse JSON data if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                data = json.loads(request.body)
            else:
                data = request.POST

            # Get form data
            first_name = data.get('first_name', '').strip()
            last_name = data.get('last_name', '').strip()
            contact = data.get('contact', '').strip()
            email = data.get('email', '').strip()
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()

            # Validate required fields
            if not all([first_name, last_name, contact, email, username, password]):
                return JsonResponse({
                    'success': False,
                    'error': 'All fields are required.'
                }) if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else render(request, 'registration/signup.html', {'error': 'All fields are required.'})

            # Validate email format
            if '@' not in email or '.' not in email:
                return JsonResponse({
                    'success': False,
                    'error': 'Please enter a valid email address.'
                }) if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else render(request, 'registration/signup.html', {'error': 'Please enter a valid email address.'})

            # Check if username already exists
            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Username already exists. Please choose a different username.'
                }) if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else render(request, 'registration/signup.html', {'error': 'Username already exists. Please choose a different username.'})

            # Check if email already exists
            if User.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Email already exists. Please use a different email address.'
                }) if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else render(request, 'registration/signup.html', {'error': 'Email already exists. Please use a different email address.'})

            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            # Add contact info to user profile (you can extend User model or use UserProfile)
            user.save()

            # Log the user in
            login(request, user)

            return JsonResponse({
                'success': True,
                'redirect_url': '/dashboard/'
            }) if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else redirect('/dashboard/')

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid data format.'
            }) if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else render(request, 'registration/signup.html', {'error': 'Invalid data format.'})
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'An error occurred during signup. Please try again.'
            }) if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else render(request, 'registration/signup.html', {'error': 'An error occurred during signup. Please try again.'})

    # GET request - show signup form
    return render(request, 'registration/signup.html')
