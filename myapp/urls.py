# myapp/urls.py - VERSION FINALE PROPRE ✅
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # ViewSets
    ProduitViewSet,
    ImageProduitViewSet, 
    SpecificationProduitViewSet,
    MouvementStockViewSet,
    CategorieViewSet,
    CommandeViewSet,
    DetailCommandeViewSet,
    NotificationViewSet,
    # Fonctions
    upload_image,
    debug_products,
    debug_images_complete,
)

# Configuration du router
router = DefaultRouter()
router.register(r'produits', ProduitViewSet, basename='produit')
router.register(r'images', ImageProduitViewSet, basename='image')
router.register(r'specifications', SpecificationProduitViewSet, basename='specification')
router.register(r'mouvements_stock', MouvementStockViewSet, basename='mouvement_stock')
router.register(r'categories', CategorieViewSet, basename='categorie')
router.register(r'commandes', CommandeViewSet, basename='commande')
router.register(r'detail-commandes', DetailCommandeViewSet, basename='detail-commande')
router.register(r'notifications', NotificationViewSet, basename='notification')

# URLs personnalisées
urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Fonctions personnalisées
    path('upload-image/', upload_image, name='upload-image'),
    path('debug-products/', debug_products, name='debug-products'),
    path('debug-images/', debug_images_complete, name='debug-images'),
]

# 📋 ROUTES DISPONIBLES :
#
# PRODUITS :
# GET/POST   /api/produits/                     - Liste/Créer produits
# GET/PUT    /api/produits/{id}/                - Détail/Modifier produit
# DELETE     /api/produits/{id}/                - Supprimer produit
# POST       /api/produits/{id}/add_image/      - Ajouter image
# POST       /api/produits/{id}/add_specification/ - Ajouter spécification  
# GET        /api/produits/{id}/images/         - Images du produit
# GET        /api/produits/{id}/specifications/ - Spécifications du produit
#
# AUTRES :
# CRUD       /api/categories/                   - Gestion catégories
# CRUD       /api/commandes/                    - Gestion commandes
# CRUD       /api/notifications/                - Gestion notifications
# CRUD       /api/images/                       - Gestion images
# CRUD       /api/specifications/               - Gestion spécifications
#
# UTILITAIRES :
# POST       /api/upload-image/                 - Upload d'images
# GET        /api/debug-products/               - Debug produits
# GET        /api/debug-images/                 - Debug images complet