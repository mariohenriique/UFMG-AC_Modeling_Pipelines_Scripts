from django.views.generic.edit import CreateView,UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.utils.safestring import mark_safe
from django.db.models import Max,Min
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib import messages
from django.conf import settings

from folium import Marker,Map,LayerControl,Icon,FeatureGroup
from folium.plugins import HeatMap
from random import randint
from datetime import date
from PIL import Image
import os

from factsheets.models import Imagens,InformacaoFamilias
from .forms import FactsheetsForm,FactsheetsUpdateForm
from formulario.models import Colecao

# Classe FactSheets que herda de TemplateView
class FactSheets(TemplateView):
    template_name = 'factsheets.html'

    # Sobrescreve o método get_context_data para fornecer dados de contexto adicionais para o template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtém uma lista de famílias distintas ordenadas e exclui aquelas que são vazias
        context['family_list'] = Colecao.objects.values('family').distinct().order_by('family').exclude(family='').exclude(family=None)

        return context

# Classe FactSheetsFamilia que herda de TemplateView
class FactSheetsFamilia(TemplateView):
    template_name = 'factsheets_familia.html'

    # Sobrescreve o método get para fornecer dados de contexto adicionais e renderizar a página
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['map'] = mark_safe(self.fazer_mapa()) # Adiciona a div do mapa ao contexto
        return render(request,self.template_name,context)

    # Sobrescreve o método get_context_data para fornecer dados de contexto para o template
    def get_context_data(self, **kwargs):
        family = self.kwargs['family']
        context = super().get_context_data(**kwargs)

        # Obtém dados relacionados à família
        distinct_genera = Colecao.objects.filter(family=family).order_by("genus").exclude(genus='').values('genus').distinct()
        context['genetic_data'] = Colecao.objects.filter(family=family).exclude(genus='').exclude(associatedSequences='').order_by('associatedSequences')
        context['genera'] = Colecao.objects.filter(genus__in=distinct_genera).values('genus').distinct().order_by('genus')
        context['species'] = Colecao.objects.filter(genus__in=context['genera']).values('genus','scientificName').distinct()
        context['family_data'] = InformacaoFamilias.objects.filter(familia=family)
        context['imagens'] = Imagens.objects.filter(familia=family)

        return context

    # Função para gerar o mapa usando a biblioteca Folium
    def fazer_mapa(self):
        family = self.kwargs['family']
        zoom_level = 4
        colecoes = Colecao.objects.filter(family=family).order_by('genus')
        genero_cores = {}
        cores = ['red','blue','green','purple','orange','darkred','lightred','beige','darkblue','darkgreen','cadetblue','darkpurple','white','pink','lightblue','lightgreen','gray','black','lightgray']

        # Lista com o maior e menor valor de latitude e longitude
        latitude_values = list(Colecao.objects.filter(family=family).aggregate(Max('decimalLatitude'),Min('decimalLatitude')).values())
        longitude_values = list(Colecao.objects.filter(family=family).aggregate(Max('decimalLongitude'),Min('decimalLongitude')).values())

        if latitude_values == [None,None] and longitude_values == [None,None]:
            latitude_values = [-19.8688655,-19.8688655]
            longitude_values = [-43.9695513,-43.9695513]
            zoom_level = 16

        # Média para determinar o meio do mapa
        latitude_media = (sum(latitude_values))/2
        longitude_media = (sum(longitude_values))/2

        # Inicializa o mapa com o meio calculado e o nível de zoom
        mapa_family = Map(location=[latitude_media,longitude_media],zoom_start=zoom_level,name='Map')
        
        # Prepara dados para o HeatMap
        heat_data = [[float(point['decimalLatitude']), float(point['decimalLongitude'])] for point in colecoes.values('decimalLatitude', 'decimalLongitude') if point['decimalLatitude'] and point['decimalLongitude']]

        for colecao in colecoes:
            if colecao.decimalLatitude and colecao.decimalLongitude:
                latitude = colecao.decimalLatitude
                longitude = colecao.decimalLongitude

                # Associa uma cor a um gênero e cria uma camada de mapa para cada gênero
                if colecao.genus not in genero_cores and len(cores) > 0:
                    cor = cores.pop(0)
                    genero_cores[colecao.genus] = cor
                    genero_camada = FeatureGroup(name='<span style="color: '+cor+';">\u25A0 </span>'+colecao.genus)
                    genero_cores[colecao.genus] = {'camada': genero_camada, 'cor': cor}
                elif len(cores) <= 0:
                    cor = "#{:06x}".format(randint(0, 0xFFFFFF))
                    genero_cores[colecao.genus] = cor
                    genero_camada = FeatureGroup(name='<span style="color: '+cor+';">\u25A0 </span>'+colecao.genus)
                    genero_cores[colecao.genus] = {'camada': genero_camada, 'cor': cor}
                else:
                    cor = genero_cores[colecao.genus]['cor']

                # Prepara informações para o popup do marcador no mapa
                texto_popup = f"UFMG-AC{colecao.catalogNumber}\n{colecao.country} ({colecao.countryCode}), {colecao.stateProvince},{colecao.county},\n {colecao.decimalLatitude};{colecao.decimalLongitude},\n{colecao.eventDate}, Col.: , Cod.: {colecao.associatedSequences}"

                # Adiciona marcadores para cada coleção ao mapa
                # Escolher o icone que será mostrado no mapa (https://getbootstrap.com/docs/3.3/components/) icon=Icon(icon='')
                Marker([latitude, longitude],popup = texto_popup,tooltip=colecao.catalogNumber,icon=Icon(color=cor),name='marker').add_to(genero_cores[colecao.genus]['camada'])

            # Adiciona as camadas de mapa para cada gênero ao mapa principal
            for genero in sorted(genero_cores.keys()):
                camada = genero_cores[genero]['camada']
                mapa_family.add_child(camada)

        # Adiciona um HeatMap ao mapa
        HeatMap(heat_data,name='HeatMap',show=False).add_to(mapa_family)

        # Adiciona um controle de camadas ao mapa
        LayerControl().add_to(mapa_family)

        # Retorna a representação HTML do mapa
        return mapa_family._repr_html_()

# Adicionar novo factsheets

# Classe FactsheetsCreate que herda de LoginRequiredMixin e CreateView
class FactsheetsCreate(LoginRequiredMixin,CreateView,):
    form_class = FactsheetsForm
    login_url = reverse_lazy('login')
    model = InformacaoFamilias
    template_name = 'add_factsheets.html'
    success_url = reverse_lazy('factsheets')

    # Sobrescreve o método post para processar o formulário de criação de factsheet
    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            # Cria uma instância de InformacaoFamilias com dados do formulário
            factsheet_familia = form.save(commit=False)

            # Atribui os dados genéticos ao campo correspondente
            factsheet_familia.dados_geneticos = self.request.POST.getlist('dados_geneticos')

            # Salva a instância do factsheet
            factsheet_familia = form.save()

            # Processa e salva as imagens associadas ao factsheet
            for image_number in range(0, self.request.POST.get('image-count-field') if type(self.request.POST.get('image-count-field')) == int else 1):
                image = request.FILES.get(f'imagens-{image_number}-image')
                legend = request.POST.get(f'imagens-{image_number}-legenda')

                if image:
                    # Cria diretório se não existir
                    path = os.path.join(settings.BASE_DIR,'static','factsheets',request.POST.get('familia'))
                    if not os.path.exists(path):
                        os.makedirs(path)

                    # Salva a imagem no diretório
                    img = Image.open(image)
                    image_name = str(date.today())+'id'+str(image_number)+image.name
                    path_img = os.path.join('factsheets',request.POST.get('familia'),image_name)
                    all_path_img = os.path.join('static',path_img)
                    img.save(all_path_img)
                    
                    # Cria e salva a instância da imagem associada ao factsheet
                    new_image = Imagens(post=factsheet_familia, familia=factsheet_familia.familia, imagens=path_img, legenda=legend)
                    new_image.save()

            return self.form_valid(form)
        else:
            self.object = None
            return self.form_invalid(form)

# UPDATE factsheets

# Classe FactsheetsUpdate que herda de LoginRequiredMixin e UpdateView
class FactsheetsUpdate(LoginRequiredMixin,UpdateView):
    login_url = reverse_lazy('login')
    template_name = 'update_factsheets.html'
    form_class = FactsheetsUpdateForm
    model = InformacaoFamilias
    success_url = reverse_lazy('factsheets')

    # Sobrescreve o método get_context_data para fornecer dados de contexto adicionais
    def get_context_data(self, **kwargs):
        family_id = self.kwargs['pk']
        family_name = InformacaoFamilias.objects.filter(id=family_id).values_list('familia')
        context = super().get_context_data(**kwargs)
        context['images'] = Imagens.objects.filter(familia__in=family_name)
        return context

    # Sobrescreve o método form_valid para processar o formulário de atualização de factsheet
    def form_valid(self, form):
        # Deletando as imagens escolhidas
        delete_images = self.request.POST.getlist('delete_image')
        if delete_images:
            for delete_image_id in delete_images:
                try:
                    image = Imagens.objects.get(pk=delete_image_id)
                    path_delete_image = os.path.join(settings.BASE_DIR,'static',str(image.imagens))
                    if os.path.exists(path_delete_image):
                        os.remove(path_delete_image)
                    image.delete()
                except Imagens.DoesNotExist:
                    pass
            messages.success(self.request, 'Images deleted successfully.')
            form = self.get_form()

        if form.is_valid():
            # Cria uma instância de InformacaoFamilias com dados do formulário
            family = form.save(commit=False)

            # Atribui os dados genéticos ao campo correspondente
            lista_dados_geneticos=[]
            for i in self.request.POST.getlist('dados_geneticos'):
                lista_dados_geneticos.append(i)
            family.dados_geneticos=lista_dados_geneticos

            # Salva a instância do factsheet
            family = form.save()

            # Processa e salva as imagens associadas ao factsheet
            for image_id in range(0, self.request.POST.get('image-count-field') if type(self.request.POST.get('image-count-field')) == int else 1):
                image = self.request.FILES.get(f'imagens-{image_id}-image')
                legend = self.request.POST.get(f'imagens-{image_id}-legenda')
                if image:
                    # Cria diretório se não existir
                    path = os.path.join(settings.BASE_DIR,'static','factsheets',self.request.POST.get('familia'))
                    if not os.path.exists(path):
                        os.makedirs(path)

                    # Salva a imagem no diretório
                    img = Image.open(image)
                    image_name = str(date.today())+'id'+str(i)+image.name
                    path_img = os.path.join('factsheets',self.request.POST.get('familia'),image_name)
                    all_path_img = os.path.join('static',path_img)
                    img.save(all_path_img)
                    
                    # Cria e salva a instância da imagem associada ao factsheet
                    new_image = Imagens(post=family, familia=family.familia, imagens=path_img, legenda=legend)
                    new_image.save()

        return super().form_valid(form)
