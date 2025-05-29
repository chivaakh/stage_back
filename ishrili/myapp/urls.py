# myapp/urls.py - AJOUTER cette route
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProduitViewSet,SpecificationProduitViewSet, MouvementStockViewSet


from .views import ProduitViewSet, ImageProduitViewSet, SpecificationProduitViewSet, upload_image

router = DefaultRouter()
router.register(r'produits', ProduitViewSet, basename='produit')
router.register(r'specifications', SpecificationProduitViewSet, basename='specification')
router.register(r'mouvements_stock', MouvementStockViewSet, basename='mouvement_stock')

urlpatterns = [
    path('', include(router.urls)),


    path('upload-image/', upload_image, name='upload-image'),  # ✅ NOUVELLE ROUTE
]
