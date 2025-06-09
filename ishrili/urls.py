# ishrili/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

# Vue simple pour la racine
def api_info(request):
    return JsonResponse({
        'message': 'API Ishrili fonctionne !',
        'version': '1.0',
        'endpoints': {
            'products': '/api/produits/',
            'categories': '/api/categories/',
            'orders': '/api/commandes/',
            'notifications': '/api/notifications/',
            'admin': '/admin/',
        }
    })

urlpatterns = [
    path('', api_info, name='api-info'),  # Page d'accueil API
    path('admin/', admin.site.urls),
    path('api/', include('myapp.urls')),
]

# Servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)