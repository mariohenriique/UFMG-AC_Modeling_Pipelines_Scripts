"""laboratorio_acarologia URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.conf.urls.static import static
from django.urls import path,include
from django.conf import settings
from django.contrib import admin

# Lista de padrões de URL que mapeiam URLs para visualizações
urlpatterns = [
    # Inclui URLs do aplicativo 'formulario'
    path('',include('formulario.urls')),

    # Inclui URLs do aplicativo 'factsheets'
    path('',include('factsheets.urls')),

    # Inclui URLs do aplicativo 'usuarios'
    path('',include('usuarios.urls')),

    # Inclui URLs do aplicativo 'paginas'
    path('',include('paginas.urls')),

    # Define a URL para a área de administração
    path('admin/', admin.site.urls),
]

# Adiciona padrões de URL para servir arquivos de mídia durante o desenvolvimento
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)