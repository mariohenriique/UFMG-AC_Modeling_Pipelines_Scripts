from django.views.generic.edit import CreateView, FormView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.contrib import messages

import pandas as pd
import chardet
import csv

from factsheets.models import *
from .forms import *
from .models import *

# Nome do template utilizado
template_formulario ='formulario.html'

# Classe para criar um novo exemplar na coleção
class ColecaoCreate(CreateView):
    # Configurações da view
    form_class = ColecaoForm
    template_name = template_formulario
    success_url = reverse_lazy('confirma_tombo')

    # Métodos para adicionar informações ao contexto
    def get_context_data(self,*args,**kwargs):
        # Chama o método da classe pai para obter o contexto padrão
        context = super().get_context_data(*args,**kwargs)

        # Adiciona informações específicas ao contexto
        context['titulo'] = 'Formulário de novos tombamentos'
        context['naologado'] = 'É necessário fazer login para salvar o registro.'
        context['avancado'] = 'Formulário de cadastro avançado.'
        context['mensagem'] = 'Preencha os campos obrigatórios.'
        context['csv'] = 'Formulário CSV <i class="material-icons">file_upload</i>'

        return context

    # Sobrescrever o método form_valid para adicionar lógica personalizada após a validação do formulário
    def form_valid(self,form):
        # Verifica se os campos necessários para calcular a coordenada de latitude estão preenchidos
        if (
            form.instance.decimalLatitude != pd.notnull
            and form.instance.graus
            and form.instance.minutos
            and form.instance.segundos
            and form.instance.Sul_Norte
        ):

            # Calcula e atualiza a coordenada de latitude no formato decimal
            form.instance.decimalLatitude = (
                form.instance.graus + form.instance.minutos/60 + form.instance.segundos/3600
            )*form.instance.Sul_Norte

        # Verifica se os campos necessários para calcular a coordenada de longitude estão preenchidos
        if (
            form.instance.decimalLongitude != pd.notnull
            and form.instance.graus_1
            and form.instance.minutos_1 
            and form.instance.segundos_1
            and form.instance.w_O
        ):

            # Calcula e atualiza a coordenada de longitude no formato decimal
            form.instance.decimalLongitude = (
                form.instance.graus_1 + form.instance.minutos_1/60 + form.instance.segundos_1/3600
            )*form.instance.w_O

        # Verifica se há uma data final de identificação e se a data de identificação está preenchida
        if form.cleaned_data['dateIdentifiedEnd'] and form.instance.dateIdentified:
            # Atualiza a data de identificação adicionando a data final
            form.instance.dateIdentified = form.instance.dateIdentified + '/' + str(form.cleaned_data['dateIdentifiedEnd'])

        # Após a validação do formulário, os dados são salvos
        url = super().form_valid(form)

        # Converte as informações das coordenadas em formato legível
        if self.object.Sul_Norte == -1:
            sulnorte = 'S'
        elif self.object.Sul_Norte == 1:
            sulnorte = 'N'

        if self.object.w_O == -1:
            lesteoeste = 'W'
        elif self.object.w_O == 1:
            lesteoeste = 'E'

        # Verifica se todos os campos necessários para gerar as coordenadas estão preenchidos
        if (
            self.object.graus
            and self.object.minutos
            and self.object.segundos
            and self.object.graus_1
            and self.object.minutos_1
            and self.object.segundos_1
            and self.object.Sul_Norte
            and self.object.w_O):

            # Cria representações verbais das coordenadas
            self.object.verbatimLatitude = str(
                str(self.object.graus) + sulnorte +''+ str(self.object.minutos) +'\''+str(self.object.segundos)+'\"'
                )

            self.object.verbatimLongitude = str(
                str(self.object.graus_1) + lesteoeste +''+ str(self.object.minutos_1) +'\''+str(self.object.segundos_1)+'\"'
                )

            # Combina as coordenadas verbais para criar a representação completa
            self.object.verbatimCoordinates = (
                self.object.verbatimLongitude + ',' + self.object.verbatimLatitude
                )

        # Verifica se há um país associado ao objeto
        if self.object.country:
            # Atualiza o código do país e o nome do país no objeto
            self.object.countryCode = self.object.country.code
            self.object.country = self.object.country.name
        
        # Verifica o scientificName
        if self.object.scientificName:
            self.object.scientificName = self.object.genus + ' ' + self.object.scientificName
            self.object.taxonRank = 'Espécie'

        elif self.object.subgenus:
            self.object.scientificName = self.object.subgenus
            self.object.taxonRank = 'Gênero'

        elif self.object.genus:
            self.object.scientificName = self.object.genus
            self.object.taxonRank = 'Gênero'
        
        elif self.object.subfamily:
            self.object.scientificName = self.object.subfamily
            self.object.taxonRank = 'Subfamília'
        
        elif self.object.family:
            self.object.scientificName = self.object.family
            self.object.taxonRank = 'Família'

        elif self.object.ordem:
            self.object.scientificName = self.object.ordem
            self.object.taxonRank = 'Ordem'

        else:
            self.object.scientificName = self.object.classe
            self.object.taxonRank = 'classe'

        # Garante que o campo 'occurrenceID' termina com o 'catalogNumber'
        if not (self.object.occurrenceID).endswith(self.object.catalogNumber):
            self.object.occurrenceID += self.object.catalogNumber
        
        # Salva as alterações no objeto
        self.object.save()

        # Retornar a URL de sucesso
        return url

    def get_success_url(self):
        # Obtém a URL de sucesso padrão usando o método da classe pai
        success_url = super().get_success_url()

        # Coleta os dados do formulário (POST) como um dicionário
        form_data = self.request.POST.dict()

        # Adiciona um par chave-valor 'query=true' aos dados do formulário
        form_data['query'] = 'true'

        # Remove o token CSRF do dicionário, pois não é necessário incluí-lo na URL
        del form_data['csrfmiddlewaretoken']

        # Cria uma string de consulta usando os dados do formulário para ser anexada à URL de sucesso
        query_string = '&'.join([f'{k}={v}' for k, v in form_data.items()])

        return f"{success_url}?{query_string}"

# Classe para criar um novo exemplar avançado na coleção, exigindo autenticação
class ColecaoAvancadoCreate(LoginRequiredMixin,CreateView):
    # Configurações da view
    login_url = reverse_lazy('login')
    model = Colecao
    form_class = ColecaoEditaForm
    template_name = template_formulario
    success_url = reverse_lazy('listar_colecao')

    # Métodos para adicionar informações ao contexto
    def get_context_data(self,*args,**kwargs):
        # Chama o método da classe pai para obter o contexto padrão
        context = super().get_context_data(*args,**kwargs)

        # Adiciona informações específicas ao contexto
        context['titulo'] = 'Formulário de tombamento'
        context['naologado'] = 'É necessário fazer login para salvar o registro.'
        context['mensagem'] = 'Cadastro Avançado da Coleção'
        context['csv'] = 'Formulário CSV <i class="material-icons">file_upload</i>'

        return context

    # Sobrescrever o método form_valid para adicionar lógica personalizada após a validação do formulário
    def form_valid(self,form):
        # Verifica se os campos relacionados à latitude estão preenchidos
        if (
            form.instance.decimalLatitude != pd.notnull
            and form.instance.graus
            and form.instance.minutos
            and form.instance.segundos
            and form.instance.Sul_Norte
            ):

            # Calcula a latitude decimal usando a fórmula fornecida
            form.instance.decimalLatitude = (
                form.instance.graus + form.instance.minutos/60 + form.instance.segundos/3600
            )*form.instance.Sul_Norte

        # Verifica se os campos relacionados à longitude estão preenchidos
        if (form.instance.decimalLongitude != pd.notnull
            and form.instance.graus_1
            and form.instance.minutos_1 
            and form.instance.segundos_1
            and form.instance.w_O
            ):

            # Calcula a longitude decimal usando a fórmula fornecida
            form.instance.decimalLongitude = (
                form.instance.graus_1 + form.instance.minutos_1/60 + form.instance.segundos_1/3600
            )*form.instance.w_O

        # Verifica se a data de identificação final está preenchida e a data de identificação principal está presente
        if form.cleaned_data['dateIdentifiedEnd'] and form.instance.dateIdentified:
            # Adiciona a data de identificação final à data de identificação principal
            form.instance.dateIdentified = form.instance.dateIdentified + '/' + str(form.cleaned_data['dateIdentifiedEnd'])

        # Chama o método da classe pai para salvar os dados do formulário
        url = super().form_valid(form)

        # Troca as informações relacionadas às coordenadas
        if self.object.Sul_Norte == -1:
            sulnorte = 'S'
        elif self.object.Sul_Norte == 1:
            sulnorte = 'N'

        if self.object.w_O == -1:
            lesteoeste = 'W'
        elif self.object.w_O == 1:
            lesteoeste = 'E'

        # Cria as representações verbais das coordenadas
        if (
            self.object.graus
            and self.object.minutos
            and self.object.segundos
            and self.object.graus_1
            and self.object.minutos_1
            and self.object.segundos_1
            and self.object.Sul_Norte
            and self.object.w_O
            ):

            self.object.verbatimLatitude = str(
                str(self.object.graus) + sulnorte +''+ str(self.object.minutos) +'\''+str(self.object.segundos)+'\"')

            self.object.verbatimLongitude = str(
                str(self.object.graus_1) + lesteoeste +''+ str(self.object.minutos_1) +'\''+str(self.object.segundos_1)+'\"')

            self.object.verbatimCoordinates = (self.object.verbatimLongitude + ',' + self.object.verbatimLatitude)

        # Verifica se há informação sobre o país
        if self.object.country:
            # Atualiza o código do país e o nome do país
            self.object.countryCode = self.object.country.code

        # Garante que o campo occurrenceID termine com o catalogNumber
        if not (self.object.occurrenceID).endswith(self.object.catalogNumber):
            self.object.occurrenceID += self.object.catalogNumber

        # Salva os dados do objeto no banco de dados
        self.object.save()

        return url

# Classe para importar dados de um arquivo CSV para o banco de dados
class ColecaoCSVCreate(FormView):
    # Configurações da view
    login_url = reverse_lazy('login')
    form_class = CsvForm
    template_name = 'formulario.html'
    success_url = reverse_lazy('listar_colecao')
    model = Colecao

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # Métodos para adicionar informações ao contexto
    def get_context_data(self,*args, **kwargs):
        # Chama o método da classe pai para obter o contexto padrão
        context = super().get_context_data(*args,**kwargs)

        # Adiciona informações específicas ao contexto
        context['titulo'] = 'Formulário CSV'
        context['modelo'] = 'tem modelo'
        context['messages'] = messages.get_messages(self.request)

        return context

    # Sobrescrever o método post para adicionar lógica de processamento do arquivo CSV
    def post(self, request,*args,**kwargs):
        def detect_encoding(file):
            rawdata = file.read(10240)
            result = chardet.detect(rawdata)
            print(result['encoding'])
            return result['encoding']
        messages.info(request, 'Iniciando o carregamento do arquivo CSV...')
        # Obtém e lê o arquivo CSV enviado no formulário
        files = request.FILES['file']
        encoding = detect_encoding(files)
        df = pd.read_csv(files,encoding=encoding)

        # Mapeia os campos do modelo com base nos campos do DataFrame
        correspondent_fields = {f.column:f for f in self.model._meta.get_fields()}
        valid_columns = [col for col in df.columns if col in correspondent_fields]
        filtered_df = df[valid_columns]
        # Converte o DataFrame para um dicionário de registros
        dict_df = filtered_df.to_dict(orient='records')

        # Função que converte dados do formato do Python para o formato do modes
        def convert_values(k,v):
            if pd.isna(v):
                v = None
            # Muda os dados das colunas S/N e W/O para números
            if correspondent_fields[k].name == "Sul_Norte" and v:
                if v == "S":
                    v = -1
                else:
                    v = 1
            elif correspondent_fields[k].name == "w_O" and v:
                if v == "W":
                    v = -1
                else:
                    v = 1
            return correspondent_fields[k].to_python(v)

        # Itera sobre cada entrada no dicionário
        for entry in dict_df:
            catalog_number = entry.get('catalogNumber')
            # Tenta obter um objeto existente ou cria um novo com base no número de catálogo
            obj, created = self.model.objects.get_or_create(catalogNumber=catalog_number)
            if not created:
                # Adiciona uma mensagem de aviso se o número de catálogo já existir
                messages.warning(self.request, f'Catalog Number {catalog_number} already exists.')

            else:
                # Atualiza os campos do objeto com os valores convertidos
                obj.__dict__.update(**{correspondent_fields[k].name: convert_values(k,v) for k,v in entry.items() if convert_values(k,v)})
                # Salva o objeto no banco de dados
                obj.save()
                messages.success(request, f'Catalog Number {catalog_number} successfully loaded.')
        return redirect(self.success_url)

# UPDATE #
# Classe para atualizar informações de um exemplar na coleção, exigindo autenticação
class ColecaoUpdate(LoginRequiredMixin,UpdateView):
    # Configurações da view
    login_url = reverse_lazy('login')
    model = Colecao
    form_class = ColecaoEditaForm
    template_name = template_formulario
    success_url = reverse_lazy('listar_colecao')

    # Sobrescrever o método form_valid para adicionar lógica personalizada após a validação do formulário
    def form_valid(self,form):
        if (
            form.instance.decimalLatitude != pd.notnull
            and form.instance.graus
            and form.instance.minutos
            and form.instance.segundos
            and form.instance.Sul_Norte
        ):

            form.instance.decimalLatitude = (
                form.instance.graus + form.instance.minutos/60 + form.instance.segundos/3600
            )*form.instance.Sul_Norte

        if (
            form.instance.decimalLongitude != pd.notnull
            and form.instance.graus_1
            and form.instance.minutos_1 
            and form.instance.segundos_1
            and form.instance.w_O
        ):

            form.instance.decimalLongitude = (
                form.instance.graus_1 + form.instance.minutos_1/60 + form.instance.segundos_1/3600
            )*form.instance.w_O

        if form.cleaned_data['dateIdentifiedEnd'] and form.instance.dateIdentified:
            form.instance.dateIdentified = form.instance.dateIdentified + '/' + str(form.cleaned_data['dateIdentifiedEnd'])

        # Após esse comando os dados são salvos
        url = super().form_valid(form)

        # Trocando as informações sobre colocar as coordenadas
        if self.object.Sul_Norte == -1:
            sulnorte = 'S'
        elif self.object.Sul_Norte == 1:
            sulnorte = 'N'

        if self.object.w_O == -1:
            lesteoeste = 'W'
        elif self.object.w_O == 1:
            lesteoeste = 'E'

        if (
            self.object.graus
            and self.object.minutos
            and self.object.segundos
            and self.object.graus_1
            and self.object.minutos_1
            and self.object.segundos_1
            and self.object.Sul_Norte
            and self.object.w_O
        ):

            self.object.verbatimLatitude = str(
                str(self.object.graus) + sulnorte +''+ str(self.object.minutos) +'\''+str(self.object.segundos)+'\"')

            self.object.verbatimLongitude = str(
                str(self.object.graus_1) + lesteoeste +''+ str(self.object.minutos_1) +'\''+str(self.object.segundos_1)+'\"')

            self.object.verbatimCoordinates = (self.object.verbatimLongitude + ',' + self.object.verbatimLatitude)

        if self.object.country:
            self.object.countryCode = self.object.country.code

        if not (self.object.occurrenceID).endswith(self.object.catalogNumber):
            self.object.occurrenceID += self.object.catalogNumber

        self.object.save()

        return url

# LIST #
# Classe para listar exemplares da coleção
class ColecaoList(ListView):
    # Configurações da view
    model = Colecao
    template_name = 'listar.html'
    paginate_by = 10
    form = ['basisOfRecord','datasetName','type','language','institutionID','institutionCode','collectionCode',
            'license','rightsHolder','dynamicProperties','occurrenceID','catalogNumber','otherCatalogNumbers','recordedBy',
            'recordNumber','individualCount','sex','lifeStage','reproductiveCondition','preparations','disposition',
            'associatedTaxa','associatedReferences','associatedMedia','associatedSequences','occurrenceRemarks','eventDate',
            'eventTime','habitat','samplingProtocol','samplingEffort','eventRemarks','continent','country','countryCode',
            'stateProvince','county','municipality','island','islandGroup','waterBody','locality','locationRemarks',
            'minimumElevationInMeters','maximumElevationInMeters','minimumDepthInMeters','maximumDepthInMeters',
            'verbatimLatitude','verbatimLongitude','decimalLatitude','decimalLongitude','coordinateUncertaintyInMeters',
            'geodeticDatum','georeferenceProtocol','georeferenceBy','georeferenceDate','georeferenceRemarks','kingdom',
            'phylum','classe','order','family','subfamily','genus','subgenus','specificEpithet','infraspecificEpithet',
            'scientificName','scientificNameAuthorShip','taxonRank','vernacularName','taxonRemarks','identificationQualifier',
            'typeStatus','identifiedBy','dateIdentified','identificationRemarks']
   
    # Método para obter o conjunto de dados a ser exibido na lista
    def get_queryset(self):
        # Recupera todos os objetos da classe Colecao ordenados pelo número de catálogo em ordem decrescente
        queryset = Colecao.objects.order_by("-catalogNumber")
        return queryset

# Classe para listar exemplares da coleção com confirmação
class TomboList(ListView):
    # Configurações da view
    model = Colecao
    template_name = 'confirma_formulario.html'

    # Método para adicionar informações ao contexto
    def get_context_data(self, **kwargs):
        # Chama o método da classe pai para obter o contexto padrão
        context = super().get_context_data(**kwargs)

        # Verifica se a query string 'query' está presente e possui o valor 'true'
        if self.request.GET.get('query') == 'true':
            # Obtém os dados do formulário da requisição e remove a chave 'query'
            form_data = self.request.GET.dict()
            form_data.pop('query')

            # Adicionar as informações do formulário ao contexto para exibição no template
            context['form_data'] = form_data

        return context

# Download #
# Classe para fazer o download de um modelo CSV para importação
class Download_Modelo(TemplateView):
    # Método para gerar e retornar o conteúdo do modelo CSV
    def colecao_csv(self):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attchment; filename=modelo_UFMGAC.csv'

        writer = csv.writer(response)

        writer.writerow(['basisOfRecord','datasetName','type','language','institutionID','institutionCode','collectionCode',
            'license','rightsHolder','dynamicProperties','occurrenceID','catalogNumber','otherCatalogNumbers','recordedBy',
            'recordNumber','individualCount','sex','lifeStage','reproductiveCondition','preparations','disposition',
            'associatedTaxa','associatedReferences','associatedMedia','associatedSequences','occurrenceRemarks','eventDate',
            'eventTime','habitat','samplingProtocol','samplingEffort','eventRemarks','continent','country','countryCode',
            'stateProvince','county','municipality','island','islandGroup','waterBody','locality','locationRemarks',
            'minimumElevationInMeters','maximumElevationInMeters','minimumDepthInMeters','maximumDepthInMeters',
            'verbatimLatitude','verbatimLongitude','decimalLatitude','decimalLongitude','coordinateUncertaintyInMeters',
            'geodeticDatum','georeferenceProtocol','georeferenceBy','georeferenceDate','georeferenceRemarks','kingdom',
            'phylum','class','order','family','subfamily','genus','subgenus','specificEpithet','infraspecificEpithet',
            'scientificName','scientificNameAuthorShip','taxonRank','vernacularName','taxonRemarks','identificationQualifier',
            'typeStatus','identifiedBy','dateIdentified','identificationRemarks'])
        return response
    
# Classe para fazer o download de etiquetas
class Download_Etiqueta(TemplateView):
    # Método para gerar e retornar o conteúdo das etiquetas
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attchment; filename=etiqueta.txt'

        writer = csv.writer(response)

        tombo = Colecao.objects.all().filter(catalogNumber=self.kwargs.get('catalog_number'))

        for i in tombo:
            writer.writerow([i.catalogNumber,i.datasetName])
        return response

# Classe para fazer o download do conjunto completo de dados em CSV
class Download(TemplateView):
    # Método para gerar e retornar o conteúdo do CSV completo
    def colecao_csv(self):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attchment; filename=UFMGAC.csv'

        writer = csv.writer(response)

        writer.writerow(['basisOfRecord','datasetName','type','language','institutionID','institutionCode','collectionCode',
            'license','rightsHolder','dynamicProperties','occurrenceID','catalogNumber','otherCatalogNumbers','recordedBy',
            'recordNumber','individualCount','sex','lifeStage','reproductiveCondition','preparations','disposition',
            'associatedTaxa','associatedReferences','associatedMedia','associatedSequences','occurrenceRemarks','eventDate',
            'eventTime','habitat','samplingProtocol','samplingEffort','eventRemarks','continent','country','countryCode',
            'stateProvince','county','municipality','island','islandGroup','waterBody','locality','locationRemarks',
            'minimumElevationInMeters','maximumElevationInMeters','minimumDepthInMeters','maximumDepthInMeters',
            'verbatimLatitude','verbatimLongitude','decimalLatitude','decimalLongitude','coordinateUncertaintyInMeters',
            'geodeticDatum','georeferenceProtocol','georeferenceBy','georeferenceDate','georeferenceRemarks','kingdom',
            'phylum','class','order','family','subfamily','genus','subgenus','specificEpithet','infraspecificEpithet',
            'scientificName','scientificNameAuthorShip','taxonRank','vernacularName','taxonRemarks','identificationQualifier',
            'typeStatus','identifiedBy','dateIdentified','identificationRemarks'])

        colecoes = Colecao.objects.all()

        # Procurar como ordenar os dados
        for colecao in colecoes:
            writer.writerow([
                colecao.basisOfRecord,colecao.datasetName,colecao.type,colecao.language,colecao.institutionID,
                colecao.institutionCode,colecao.collectionCode,colecao.license,colecao.rightsHolder,colecao.dynamicProperties,
                colecao.occurrenceID,colecao.catalogNumber,colecao.otherCatalogNumbers,colecao.recordedBy,colecao.recordNumber,
                colecao.individualCount,colecao.sex,colecao.lifeStage,colecao.reproductiveCondition,colecao.preparations,
                colecao.disposition,colecao.associatedTaxa,colecao.associatedReferences,colecao.associatedMedia,
                colecao.associatedSequences,colecao.occurrenceRemarks,colecao.eventDate,colecao.eventTime,colecao.habitat,
                colecao.samplingProtocol,colecao.samplingEffort,colecao.eventRemarks,colecao.continent,colecao.country,
                colecao.countryCode,colecao.stateProvince,colecao.county,colecao.municipality,colecao.island,
                colecao.islandGroup,colecao.waterBody,colecao.locality,colecao.locationRemarks,colecao.minimumElevationInMeters,
                colecao.maximumElevationInMeters,colecao.minimumDepthInMeters,colecao.maximumDepthInMeters,
                colecao.verbatimLatitude,colecao.verbatimLongitude,colecao.decimalLatitude,colecao.decimalLongitude,
                colecao.coordinateUncertaintyInMeters,colecao.geodeticDatum,colecao.georeferenceProtocol,colecao.georeferenceBy,
                colecao.georeferenceDate,colecao.georeferenceRemarks,colecao.kingdom,colecao.phylum,colecao.classe,
                colecao.order,colecao.family,colecao.subfamily,colecao.genus,colecao.subgenus,colecao.specificEpithet,
                colecao.infraspecificEpithet,colecao.scientificName,colecao.scientificNameAuthorShip,colecao.taxonRank,
                colecao.vernacularName,colecao.taxonRemarks,colecao.identificationQualifier,colecao.typeStatus,
                colecao.identifiedBy,colecao.dateIdentified,colecao.identificationRemarks
            ])

        return response