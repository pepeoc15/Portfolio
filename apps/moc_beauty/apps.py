from django.apps import AppConfig


class MocBeautyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.moc_beauty'
    label = 'moc_beauty'
    
    def ready(self):
        import moc_beauty.signals
