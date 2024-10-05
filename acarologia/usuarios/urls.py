from django.contrib.auth import views as auth_views
from django.urls import path

from .views import *

# Define os padrões de URL para diferentes visualizações
urlpatterns = [
    # URL para a visualização de login usando a classe LoginView fornecida pelo Django
    path('login/',auth_views.LoginView.as_view(template_name='login.html'),name='login'),

    # URL para a visualização de logout usando a classe LogoutView fornecida pelo Django
    path('logout/',auth_views.LogoutView.as_view(template_name='logout.html'),name='logout'),

    # URL para a visualização da página do usuário usando a classe PaginaUsuario definida no aplicativo
    path('usuario/',PaginaUsuario.as_view(),name='paginausuario'),

    # URL para a visualização de alteração de senha usando a classe AlterarSenha definida no aplicativo
    path('alterar-senha/', AlterarSenha.as_view(),name='alterarsenha'),

    # URL para a visualização de confirmação de alteração de senha usando a classe SenhaAlterada definida no aplicativo
    path('alterar-senha/concluido', SenhaAlterada.as_view(),name='senhaalterada'),
]