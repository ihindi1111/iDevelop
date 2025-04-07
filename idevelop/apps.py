from django.apps import AppConfig


class IdevelopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'idevelop'

class GoogleLoginConfig(AppConfig):
    name = 'google_login'
