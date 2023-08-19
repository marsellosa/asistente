from django.contrib.auth.views import * #type:ignore
from django.urls import path
from home.views import *

app_name = 'home'

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('reset_password/', PasswordResetView.as_view(template_name='apps/home/forgot_password.html'), name='reset_password'),
    path('reset_password_sent/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='apps/home/recover_password.html'), name='password_reset_confirm'),
    path('reset_password_complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
