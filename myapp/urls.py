from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
<<<<<<< HEAD
from .import views
from .views import ProduitViewSet
from .views import ProduitViewSet, ImageProduitViewSet, SpecificationProduitViewSet
from .views import ProduitViewSet,SpecificationProduitViewSet, MouvementStockViewSet
from rest_framework.routers import DefaultRouter
from .views import CommandeViewSet, DetailCommandeViewSet
from .views import NotificationViewSet

from .views import ProduitViewSet, ImageProduitViewSet, SpecificationProduitViewSet, upload_image
=======
from . import views
from .views import (
    ProduitViewSet, ImageProduitViewSet, SpecificationProduitViewSet, 
    MouvementStockViewSet, CategorieViewSet, NotificationViewSet,
     upload_image
)
>>>>>>> 7e08b3a922f02d8948a143a1aa440910b206d999

router = DefaultRouter()
router.register(r'produits', ProduitViewSet, basename='produit')
router.register(r'specifications', SpecificationProduitViewSet, basename='specification')
router.register(r'mouvements_stock', MouvementStockViewSet, basename='mouvement_stock')
router.register(r'categories', CategorieViewSet, basename='categorie')
<<<<<<< HEAD

router.register(r'commandes', CommandeViewSet)
router.register(r'detail-commandes', DetailCommandeViewSet)

=======
>>>>>>> 7e08b3a922f02d8948a143a1aa440910b206d999
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('upload-image/', upload_image, name='upload-image'),
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


    

