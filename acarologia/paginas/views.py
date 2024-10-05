from django.views.generic import TemplateView

# Create your views here.

class PaginaInicial(TemplateView):
    template_name = 'homepage.html'

class Equipe(TemplateView):
    template_name = 'equipe.html'