from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto login the user
            login(request, user)
            messages.success(request, "Registration successful")
            return redirect("/")
        else:
            messages.error(request, "Registration failed")
    else:
        form = UserCreationForm()
    
    return render(request, "accounts/register.html", {"form": form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect("/")
    
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful")
                return redirect("/")
        else:
            messages.error(request, "Invalid username or password")
    else:
        form = AuthenticationForm()
    
    return render(request, "accounts/login.html", {"form": form})

@login_required
def profile(request):
    return render(request, "accounts/profile.html")

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "Logout successful")
    return redirect("accounts:login")

def home(request):
    return render(request, "accounts/home.html")

# Create your views here.
