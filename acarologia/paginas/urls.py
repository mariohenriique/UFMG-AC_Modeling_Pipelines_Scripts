from django.urls import path
from .views import *

# Define os padrões de URL para o aplicativo
urlpatterns = [
    # Caminho para a visualização da página inicial
    path('',PaginaInicial.as_view(),name='homepage'),

    # Caminho para a visualização da equipe
    path('equipe/',Equipe.as_view(),name='equipe'),
]
