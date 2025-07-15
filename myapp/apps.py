# apps.py
from django.apps import AppConfig

class MyappConfig(AppConfig): 
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp' 
    verbose_name = 'Ishrili E-Commerce'
    
    def ready(self):
        """Importation des signaux quand l'app est prête"""
        try:
            import myapp.signals  
            print("✅ Signaux chargés avec succès")
        except ImportError as e:
            print(f"❌ Erreur lors du chargement des signaux: {e}")
        except Exception as e:
            print(f"⚠️  Erreur inattendue lors du chargement des signaux: {e}")