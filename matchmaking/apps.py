from django.apps import AppConfig
from firebase_admin import credentials, initialize_app
import firebase_admin


class MatchmakingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'matchmaking'
