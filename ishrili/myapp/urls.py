# myapp/urls.py - VERSION CORRIGÉE

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProduitViewSet,SpecificationProduitViewSet, MouvementStockViewSet



router = DefaultRouter()
router.register(r'produits', ProduitViewSet, basename='produit')
router.register(r'specifications', SpecificationProduitViewSet, basename='specification')
router.register(r'mouvements_stock', MouvementStockViewSet, basename='mouvement_stock')

urlpatterns = [
    path('', include(router.urls)),
]

