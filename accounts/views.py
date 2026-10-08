from django.shortcuts import render, redirect
from django.contrib.auth import logout

def login_view(request):
    return render(request, 'landing.html')

def register_view(request):
    return render(request, 'landing.html')

def logout_view(request):
    logout(request)
    return redirect('dashboard:landing')

def profile_view(request):
    return render(request, 'landing.html')
