# ✅ 2. MODIFIER ishrili/urls.py (urls.py du projet principal)

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
        'media_url': settings.MEDIA_URL,  # ← AJOUTÉ pour debug
        'endpoints': {
            'products': '/api/produits/',
            'categories': '/api/categories/',
            'orders': '/api/commandes/',
            'notifications': '/api/notifications/',
            'upload': '/api/upload-image/',  # ← AJOUTÉ
            'admin': '/admin/',
        }
    })

urlpatterns = [
    path('', api_info, name='api-info'),
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),
    path('api/', include('myapp.urls')),
]

# ✅ ESSENTIEL : Servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # ✅ AJOUT : Log pour debug
    print(f"🖼️  MEDIA_URL: {settings.MEDIA_URL}")
    print(f"📁 MEDIA_ROOT: {settings.MEDIA_ROOT}")