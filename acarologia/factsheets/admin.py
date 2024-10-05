from factsheets.models import InformacaoFamilias,Imagens
from django.contrib import admin

class MultipleImage(admin.ModelAdmin):
    class ImageInline(admin.TabularInline):
        model = Imagens
    inlines = [
        ImageInline,
    ]

# Registra o modelo InformacaoFamilias com a configuração personalizada MultipleImage
admin.site.register(InformacaoFamilias,MultipleImage)