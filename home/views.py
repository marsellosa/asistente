from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from home.forms import CreateUserForm
from home.decorators import unauthenticated_user
from allauth.account.views import (
    LoginView as AllauthLoginView, 
    SignupView as AllauthSignupView, 
    LogoutView as AllauthLogoutView,
    PasswordResetView as AllauthPasswordResetView,
    PasswordResetDoneView as AllauthPasswordResetDoneView,
    PasswordResetFromKeyView as AllauthPasswordResetFromKeyView,
    PasswordResetFromKeyDoneView as AllauthPasswordResetFromKeyDoneView
)

class LoginView(AllauthLoginView):
    template_name = 'apps/home/login.html'

class SignupView(AllauthSignupView):
    template_name = 'apps/home/register.html'

class LogoutView(AllauthLogoutView):
    pass

class PasswordResetView(AllauthPasswordResetView):
    template_name = 'apps/home/forgot_password.html'

class PasswordResetDoneView(AllauthPasswordResetDoneView):
    template_name = 'apps/home/password_reset_done.html'

class PasswordResetFromKeyView(AllauthPasswordResetFromKeyView):
    template_name = 'apps/home/password_reset_confirm.html'

class PasswordResetFromKeyDoneView(AllauthPasswordResetFromKeyDoneView):
    template_name = 'apps/home/password_reset_complete.html'

def home_view(request):
    if request.user.is_authenticated:
        return redirect('main:inicio')
    return render(request, 'apps/home/login.html') # Redirect to login if not authenticated


def check_password_match(request):
    context, template = {}, 'apps/home/partials/password_input.html'
    if not request.htmx:
        raise Http404
    
    password1 = request.POST.get("password1", "")
    password2 = request.POST.get("new_password2", "")
    
    if password1 != password2:
        return HttpResponse('<p>Las contraseñas no coinciden.</p>')
    
    return HttpResponse('')
