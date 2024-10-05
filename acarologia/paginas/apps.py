from django.apps import AppConfig

class PaginasConfig(AppConfig):
    # Define a chave padrão_auto_field para 'django.db.models.BigAutoField'
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Define o nome do aplicativo como 'paginas'
    name = 'paginas'
