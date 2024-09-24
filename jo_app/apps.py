"""
Ce module gère la configuration de l'application.
"""
from django.apps import AppConfig


class JoAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "jo_app"
