from django.apps import AppConfig

class UsuariosConfig(AppConfig):
    # Define o campo de autoincremento padrão para modelos deste aplicativo.
    default_auto_field = 'django.db.models.BigAutoField'

    # Define o nome do aplicativo.
    name = 'usuarios'