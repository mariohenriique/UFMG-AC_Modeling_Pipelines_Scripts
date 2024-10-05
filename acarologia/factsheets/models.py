from django.db import models

import os

def get_upload_path(instance, filename):
    return os.path.join('factsheets', instance.post.familia)

# Define o modelo InformacaoFamilias
class InformacaoFamilias(models.Model):
    ano = models.IntegerField(help_text="Selecione o ano")
    autor = models.CharField(max_length=50)
    caracteristicas_gerais = models.TextField(verbose_name="Características Gerais",default="")
    diagnoses = models.TextField(verbose_name="Diagnoses")
    dados_geneticos = models.TextField(verbose_name="Dados genéticos",blank=True,null=True)
    familia = models.CharField(max_length=50,verbose_name='Família',unique=True)
    referencias = models.TextField(verbose_name="Referências",default="")

    def __str__(self):
        return f"{self.familia}"

# Define o modelo Imagens usando uma chave estrangeira para InformacaoFamilias
class Imagens(models.Model):
    post = models.ForeignKey(InformacaoFamilias, on_delete=models.CASCADE, related_name='imagens')
    # Este campo é para acessar a família
    familia = models.CharField(max_length=50,verbose_name='Família',null=True)
    imagens = models.ImageField('Imagem',blank=True,upload_to=get_upload_path)
    legenda = models.TextField(verbose_name="Legenda",default="",blank=True)

# Define o modelo Taxon para os identificadores únicos e posteriormente fazer a arvore de famílias
class Taxon(models.Model):
    nome = models.CharField(max_length=50)
    taxonID = models.CharField(max_length=50,verbose_name='taxon ID',blank=True)
    taxon = models.CharField(max_length=50,verbose_name='Taxon',blank=True)
    txID_pai = models.CharField(max_length=50,verbose_name='ID superior',blank=True)
    txID_filho = models.CharField(max_length=50,verbose_name='ID inferior',blank=True)
    filho = models.ManyToManyField('self',max_length=50,verbose_name='Índice filho',blank=True)
    pai = models.ForeignKey('self', related_name='filhos', on_delete=models.CASCADE, null=True, blank=True)
