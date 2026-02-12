
from django.urls import path
from home.views import *

# app_name = 'home'

# from allauth.account.views import (
#     LoginView, SignupView, LogoutView, 
#     PasswordResetView, PasswordResetDoneView, 
#     PasswordResetFromKeyView, PasswordResetFromKeyDoneView
# )

# urlpatterns = [
#     path('', home_view, name='home'),
#     path('login/', LoginView.as_view(), name='login'),
#     path('logout/', LogoutView.as_view(), name='logout'),
#     path('register/', SignupView.as_view(), name='register'),
#     path('hx/password_check_match/', check_password_match, name='check_password_match'),
#     path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
#     path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
#     path('reset/<uidb64>/<token>/', PasswordResetFromKeyView.as_view(), name='password_reset_confirm'),
#     path('password_reset_complete/', PasswordResetFromKeyDoneView.as_view(), name='password_reset_complete'),
# ]
