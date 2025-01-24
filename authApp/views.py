# views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib.auth.models import User
from .forms import RegisterForm
from supabase import create_client, Client
import os

# Initialize Supabase client
url = os.getenv('SUPABASE_URL')
key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
supabase: Client = create_client(url, key)

# User Registration
# def register_user(request):
#     if request.method == "POST":
#         form = RegisterForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get("username")
#             password = form.cleaned_data.get("password")

#             # Register the user in Supabase
#             user = supabase.auth.sign_up({
#                 'email': username,
#                 'password': password
#             })

#             if user:
#                 login(request, user)
#                 return redirect('home')
#     else:
#         form = RegisterForm()
#     return render(request, 'accounts/register.html', {'form': form})

def register_user(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            try:
                response = supabase.auth.sign_up({
                    'email': email,
                    'password': password
                })

                # Sync user with Django's User model (optional)
                if response.get('user'):
                    user = User.objects.create_user(username=email, email=email, password=password)
                    login(request, user)
                    return redirect('home')
                else:
                    form.add_error(None, "Registration failed. Please try again.")
            except Exception as e:
                form.add_error(None, f"Error during registration: {str(e)}")
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


# User Login
# def login_view(request):
#     error_message = None
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")
        
#         # Attempt to sign in with Supabase
#         try:
#             user = supabase.auth.sign_in({
#                 'email': username,
#                 'password': password
#             })
            
#             if user:
#                 login(request, user)
#                 next_url = request.POST.get('next') or request.GET.get('next') or 'home'
#                 return redirect(next_url)
#             else:
#                 error_message = "Invalid Credentials!"
#         except Exception as e:
#             error_message = f"Error during login: {str(e)}"
    
#     return render(request, 'accounts/login.html', {'error': error_message})

def login_view(request):
    error_message = None
    if request.method == "POST":
        email = request.POST.get("username")
        password = request.POST.get("password")
        
        try:
            response = supabase.auth.sign_in({
                'email': email,
                'password': password
            })

            # Check if login was successful
            if response.get('user'):
                # Optionally, sync with Django's User model
                user, created = User.objects.get_or_create(username=email, email=email)
                if created:
                    user.set_password(password)
                    user.save()

                login(request, user)
                return redirect(request.GET.get('next', 'home'))
            else:
                error_message = "Invalid email or password."
        except Exception as e:
            error_message = f"Error during login: {str(e)}"

    return render(request, 'accounts/login.html', {'error': error_message})



# User Logout
def logout_view(request):
    logout(request)
    return redirect('login')

# Home View (Protected)
@login_required
def home_view(request):
    return render(request, 'auth1_app/home.html')

# Protected View using Class-Based View
class ProtectedView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        return render(request, 'registration/protected.html')
