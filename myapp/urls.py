# myapp/urls.py - VERSION CORRIGÉE

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .import views
from .views import ProduitViewSet
from .views import ProduitViewSet, ImageProduitViewSet, SpecificationProduitViewSet

router = DefaultRouter()
router.register(r'produits', ProduitViewSet, basename='produit')
router.register(r'images', ImageProduitViewSet, basename='image')
router.register(r'specifications', SpecificationProduitViewSet, basename='specification')

urlpatterns = [
    path('', include(router.urls)),
    # path('test/', views.test_api, name='test_api'),
]


# Routes disponibles après cette configuration :
# GET/POST   /api/produits/                     - Liste/Créer produits
# GET/PUT    /api/produits/{id}/                - Détail produit
# POST       /api/produits/{id}/add_image/      - Ajouter image
# POST       /api/produits/{id}/add_specification/ - Ajouter spécification  
# GET        /api/produits/{id}/images/         - Images du produit
# GET        /api/produits/{id}/specifications/ - Spécifications du produit
# CRUD       /api/images/                       - Gestion images
# CRUD       /api/specifications/               - Gestion spécifications
