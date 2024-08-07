"""tgbot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('bot1075118916/', include('bot.urls')),
    path('comanda/', include('comanda.urls')),
    path('consumos/', include('consumos.urls')),
    path('main/', include('main.urls')),
    path('operadores/', include('operadores.urls')),
    path('pedidos/', include('pedidos.urls')),
    path('personas/', include('persona.urls')),
    path('prepagos/', include('prepagos.urls')),
    path('productos/', include('productos.urls')),
    path('recetas/', include('recetas.urls')),
    path('reportes/', include('reportes.urls')),
    path('socios/', include('socios.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
