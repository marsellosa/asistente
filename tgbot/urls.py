from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from django.views.generic import TemplateView
from django.views.static import serve
import os
from home.views import (
    home_view, check_password_match,
    LoginView, SignupView, LogoutView,
    PasswordResetView, PasswordResetDoneView,
    PasswordResetFromKeyView, PasswordResetFromKeyDoneView
)


urlpatterns = [
    path('service-worker.js', serve, {'document_root': settings.STATICFILES_DIRS[0], 'path': 'service-worker.js'}),
    path('main/service-worker.js', serve, {'document_root': settings.STATICFILES_DIRS[0], 'path': 'service-worker.js'}),
    path('favicon.ico', serve, {'document_root': settings.STATICFILES_DIRS[0], 'path': 'favicon.ico'}),
    path('admin/', admin.site.urls),
    # path('', include('home.urls')),
    path('', home_view, name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', SignupView.as_view(), name='register'),
    path('hx/password_check_match/', check_password_match, name='check_password_match'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetFromKeyView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/', PasswordResetFromKeyDoneView.as_view(), name='password_reset_complete'),

    path('accounts/', include('allauth.urls')),
    path('bot1075118916/', include('bot.urls')),
    # path('clubes/', include('clubes.urls')),
    path('comanda/', include('comanda.urls')),
    path('consumos/', include('consumos.urls')),
    # path('evaluaciones/', include('evaluaciones.urls')),
    # path('finanzas/', include('finanzas.urls')),
    path('main/', include('main.urls')),
    # path('notificaciones/', include('notificaciones.urls')),
    path('operadores/', include('operadores.urls')),
    path('pedidos/', include('pedidos.urls')),
    path('personas/', include('persona.urls')),
    path('prepagos/', include('prepagos.urls')),
    path('productos/', include('productos.urls')),
    path('recetas/', include('recetas.urls')),
    path('reportes/', include('reportes.urls')),
    path('socios/', include('socios.urls')),
    path('whatsapp/', include('whatsapp.urls')),
] #+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])