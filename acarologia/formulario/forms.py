from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from django import forms

from .models import *

# Formulário para adicionar novas instâncias de Colecao
class ColecaoForm(forms.ModelForm):
    # Campos adicionais para Data do evento final, Data georeferenciamento final e Data de identificação final
    eventDateEnd = forms.DateField(required=False,label='Data do evento final',widget=forms.DateInput(attrs={'type': 'date'}))
    georeferenceDateEnd = forms.DateField(required=False,label='Data georeferenciamento final',widget=forms.DateInput(attrs={'type': 'date'}))
    dateIdentifiedEnd = forms.DateField(required=False,label='Data de identificação final',widget=forms.DateInput(attrs={'type': 'date','min':'{{ today }}'}))

    # Verificar o country
    # Campo de país usando a biblioteca django-countries
    country = CountryField(blank=True, null=True,verbose_name="País",default="BR").formfield()

    class Meta:
        model = Colecao
        # Lista completa de campos do modelo Colecao
        fields = ['catalogNumber','otherCatalogNumbers','recordedBy','recordNumber','individualCount','sex','lifeStage',
            'reproductiveCondition','preparations','associatedTaxa','associatedReferences','associatedMedia','associatedSequences',
            'occurrenceRemarks','eventDate','eventDateEnd','eventTime','habitat','samplingProtocol','samplingEffort','eventRemarks',
            'continent','country','stateProvince','county','municipality','locality','waterBody',
            'locationRemarks','minimumElevationInMeters','maximumElevationInMeters','minimumDepthInMeters','maximumDepthInMeters',
            'verbatimLatitude','verbatimLongitude','verbatimCoordinates','decimalLatitude','decimalLongitude',
            'coordinateUncertaintyInMeters','geodeticDatum','georeferenceProtocol','georeferenceBy','georeferenceDate',
            'georeferenceDateEnd','georeferenceRemarks','kingdom','phylum','classe','order','family','subfamily','genus','subgenus',
            'specificEpithet','infraspecificEpithet','scientificName','scientificNameAuthorShip','taxonRank','vernacularName',
            'taxonRemarks','identificationQualifier','typeStatus','identifiedBy','dateIdentified','dateIdentifiedEnd',
            'identificationRemarks']

        # Configurar widgets para alguns campos específicos
        if Colecao.objects.last():
            widgets = {
            'eventDate': forms.DateInput(attrs={'type': 'date'}),
            'georeferenceDate': forms.DateInput(attrs={'type': 'date'}),
            'dateIdentified': forms.DateInput(attrs={'type': 'date','id':'dateIdentified'}),
            'eventTime': forms.TimeInput(attrs={'type': 'time'}),
            'catalogNumber': forms.TextInput(attrs={'placeholder': int(str(Colecao.objects.last()).split('-')[-1])+1}),
        }

# Formulário para editar instâncias existentes de Colecao
class ColecaoEditaForm(forms.ModelForm):
    # Campos adicionais para Data do evento final, Data georeferenciamento final e Data de identificação final
    eventDateEnd = forms.DateField(required=False,widget=forms.DateInput(attrs={'type': 'date'}))
    georeferenceDateEnd = forms.DateField(required=False,widget=forms.DateInput(attrs={'type': 'date'}))
    dateIdentifiedEnd = forms.DateField(required=False,widget=forms.DateInput(attrs={'type': 'date'}))

    # Campo de país usando a biblioteca django-countries
    country = CountryField(blank=True, null=True,verbose_name="País")

    class Meta:
        model=Colecao
        # Lista completa de campos do modelo Colecao para edição
        fields = ['basisOfRecord','datasetName','type','language','institutionID','institutionCode','collectionCode',
            'license','rightsHolder','dynamicProperties','occurrenceID','catalogNumber','otherCatalogNumbers','recordedBy',
            'recordNumber','individualCount','sex','lifeStage','reproductiveCondition','preparations','disposition','associatedTaxa',
            'associatedReferences','associatedMedia','associatedSequences','occurrenceRemarks','eventDate','eventTime','habitat',
            'samplingProtocol','samplingEffort','eventRemarks','continent','country','countryCode','stateProvince','county',
            'municipality','island','islandGroup','waterBody','locality','locationRemarks','minimumElevationInMeters',
            'maximumElevationInMeters','minimumDepthInMeters','maximumDepthInMeters','verbatimLatitude','verbatimLongitude',
            'graus','minutos','segundos','Sul_Norte','graus_1','minutos_1','segundos_1','w_O','verbatimCoordinates',
            'decimalLatitude','decimalLongitude','coordinateUncertaintyInMeters','geodeticDatum','georeferenceProtocol',
            'georeferenceBy','georeferenceDate','georeferenceRemarks','kingdom','phylum','classe','order','family','subfamily',
            'genus','subgenus','specificEpithet','infraspecificEpithet','scientificName','scientificNameAuthorShip','taxonRank',
            'vernacularName','taxonRemarks','identificationQualifier','typeStatus','identifiedBy','dateIdentified',
            'dateIdentifiedEnd','identificationRemarks']

        # Configurar widgets para alguns campos específicos
        if Colecao.objects.last():
            widgets = {
            'eventDate': forms.DateInput(attrs={'type': 'date'}),
            'georeferenceDate': forms.DateInput(attrs={'type': 'date'}),
            'dateIdentified': forms.DateInput(attrs={'type': 'date'}),
            'eventTime': forms.TimeInput(attrs={'type': 'time'}),
            'catalogNumber': forms.TextInput(attrs={
                'placeholder': int(str(Colecao.objects.last()).split('-')[-1])+1}),
        }

# Formulário para upload de arquivo CSV relacionado à Colecao
class CsvForm(forms.ModelForm):
    # Campo para o arquivo CSV
    file = forms.FileField(label='arquivo')

    class Meta:
        model = Colecao
        fields = ['file']