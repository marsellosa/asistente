from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from home.forms import CreateUserForm
from home.decorators import unauthenticated_user

def home_view(request):
    context, template  = {}, 'apps/home/home.html'
    return render(request, template, context)

@unauthenticated_user
def login_view(request):
    context, template  = {}, 'apps/home/login.html'
    if request.method == 'POST':
        
        user = authenticate(
            request, 
            username = request.POST.get('username'),
            password = request.POST.get('password')
            )
        if user is not None:
            login(request, user)
            return redirect('main:inicio')
        else:
            messages.info(request, f"Username or Password is incorrect")
    return render(request, template, context)

@unauthenticated_user
def register_view(request):
    context, template = {}, 'apps/home/register.html'
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('email')
            messages.success(request, f"Account was created for {username}")
            return redirect('home:login')

    context['form'] = form
    return render(request, template, context)

def logout_view(request):
    logout(request)
    return redirect('home:login')