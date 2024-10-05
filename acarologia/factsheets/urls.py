from django.urls import path,re_path
from .views import *

urlpatterns = [
    # Define uma URL usando re_path para visualizar informações de famílias específicas
    path('factsheets/<str:family>', FactSheetsFamilia.as_view(), name='factsheetsfamilia'),

    # Define uma URL para editar factsheets usando um ID específico
    path('editar/factsheets/<int:pk>/',FactsheetsUpdate.as_view(),name='editar_factsheet'),

    # Define uma URL para cadastrar novos factsheets
    path('cadastrar/factsheets/',FactsheetsCreate.as_view(),name='adicionarfactsheet'),

    # Define uma URL para visualizar todos os factsheets
    path('factsheets/',FactSheets.as_view(),name='factsheets'),
]