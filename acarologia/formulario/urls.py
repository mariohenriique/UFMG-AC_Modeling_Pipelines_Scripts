from django.urls import path
from .views import *

urlpatterns = [
    # URL para cadastrar coleção de forma avançada
    path('cadastrar/avancado/colecao/',ColecaoAvancadoCreate.as_view(),name='cadastrar_avancado_colecao'),

    # URL para cadastrar coleção a partir de um arquivo CSV
    path('cadastrar/csv/colecao/',ColecaoCSVCreate.as_view(),name='cadastrar_csv_colecao'),

    # URL para editar coleção específica usando seu ID (pk)
    path('editar/colecao/<int:pk>/',ColecaoUpdate.as_view(),name='editar_colecao'),

    # URL para cadastrar nova coleção
    path('cadastrar/colecao/',ColecaoCreate.as_view(),name='cadastrar_colecao'),

    # URL para listar todas as coleções
    path('listar/colecao/',ColecaoList.as_view(),name='listar_colecao'),

    # URL para confirmar tombo
    path('confirma/tombo/',TomboList.as_view(),name='confirma_tombo'),

    # URL para baixar etiqueta de uma coleção específica usando seu número de catálogo
    path('etiqueta/<str:catalog_number>/',Download_Etiqueta.as_view(),name='baixa_etiqueta'),

    # URL para baixar o modelo (template) do arquivo CSV
    path('modelo/',Download_Modelo.colecao_csv,name='baixa_modelo'),

    # URL para baixar a coleção em formato CSV
    path('download/',Download.colecao_csv,name='baixa'),
]