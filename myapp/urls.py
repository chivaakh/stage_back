from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProduitViewSet, ImageProduitViewSet, SpecificationProduitViewSet,
    MouvementStockViewSet, CategorieViewSet, NotificationViewSet,
    ClientProduitViewSet, ClientCategorieViewSet, PanierViewSet,
    FavoriViewSet, AvisViewSet, ClientCommandeViewSet, ClientProfilViewSet,
    CommandeViewSet, DetailCommandeViewSet,
    upload_image
)

router = DefaultRouter()

# Frontend client routes
router.register(r'client/produits', ClientProduitViewSet, basename='client-produits')
router.register(r'client/categories', ClientCategorieViewSet, basename='client-categories')
router.register(r'client/panier', PanierViewSet, basename='panier')
router.register(r'client/favoris', FavoriViewSet, basename='favoris')
router.register(r'client/avis', AvisViewSet, basename='avis')
router.register(r'client/commandes', ClientCommandeViewSet, basename='client-commandes')
router.register(r'client/profil', ClientProfilViewSet, basename='client-profil')

# Admin or shared routes
router.register(r'produits', ProduitViewSet, basename='produit')
router.register(r'specifications', SpecificationProduitViewSet, basename='specification')
router.register(r'mouvements_stock', MouvementStockViewSet, basename='mouvement_stock')
router.register(r'categories', CategorieViewSet, basename='categorie')
router.register(r'commandes', CommandeViewSet, basename='commandes')  # 🟢 important pour /commandes/<id>/tracking/
router.register(r'detail-commandes', DetailCommandeViewSet)
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('upload-image/', upload_image, name='upload-image'),
]
