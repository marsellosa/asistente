from django.contrib.auth.views import * #type:ignore
from django.urls import path, reverse_lazy
from home.views import *

# app_name = 'home'

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('hx/password_check_match/', check_password_match, name='check_password_match'),
    path('password_reset/', PasswordResetView.as_view(
            template_name='apps/home/forgot_password.html', 
            email_template_name='apps/home/password_reset_email.html',
            subject_template_name='apps/home/password_reset_subject.txt',
        ), 
        name='password_reset'
    ),
    path('password_reset/done/', PasswordResetDoneView.as_view(
            template_name='apps/home/password_reset_done.html',
        ), 
        name='password_reset_done'
    ),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
            template_name='apps/home/password_reset_confirm.html',
            success_url=reverse_lazy('password_reset_complete')
        ), 
        name='password_reset_confirm'),
    path('password_reset_complete/', PasswordResetCompleteView.as_view(template_name='apps/home/password_reset_complete.html'), name='password_reset_complete'),
]
