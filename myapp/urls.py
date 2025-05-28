from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .import views

router = DefaultRouter()
router.register(r'utilisateurs', UtilisateurViewSet)
router.register(r'images-utilisateur', ImageUtilisateurViewSet)
router.register(r'clients', DetailsClientViewSet)
router.register(r'commercants', DetailsCommercantViewSet)
router.register(r'categories', CategorieViewSet)
router.register(r'produits', ProduitViewSet)
router.register(r'images-produit', ImageProduitViewSet)
router.register(r'specifications', SpecificationProduitViewSet)
router.register(r'commandes', CommandeViewSet)
router.register(r'details-commande', DetailCommandeViewSet)
router.register(r'avis', AvisViewSet)
router.register(r'paniers', PanierViewSet)
router.register(r'favoris', FavoriViewSet)
router.register(r'mouvements-stock', MouvementStockViewSet)
router.register(r'journal-admin', JournalAdminViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('test/', views.test_api, name='test_api'),
]
