# dashboard/views.py
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm

def home(request):
    return render(request, 'home_app/home.html')

def home_logedIn(request):
    return render(request, 'home_app/home_logedIn.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home_logedIn')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'home_app/login.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'home_app/register.html', {'form': form})