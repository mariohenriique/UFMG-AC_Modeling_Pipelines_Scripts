from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.urls import reverse_lazy

# Create your views here.

# Classe de visualização para a página de login
class Login(TemplateView):
    template_name = 'login.html'

# Classe de visualização para a página do usuário
class PaginaUsuario(TemplateView):
    template_name = 'usuario.html'

# Classe de visualização para a alteração de senha, requer autenticação (LoginRequiredMixin)
class AlterarSenha(LoginRequiredMixin,PasswordChangeView):
    template_name = 'alterar_senha.html'
    success_url = reverse_lazy('senhaalterada')

# Classe de visualização para a página de confirmação de alteração de senha, requer autenticação (LoginRequiredMixin)
class SenhaAlterada(LoginRequiredMixin,PasswordChangeDoneView):
    template_name = 'senha_alterada.html'