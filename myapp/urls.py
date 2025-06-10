from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .import views
from .views import ProduitViewSet
from .views import ProduitViewSet, ImageProduitViewSet, SpecificationProduitViewSet
from .views import ProduitViewSet,SpecificationProduitViewSet, MouvementStockViewSet
from rest_framework.routers import DefaultRouter
from .views import CommandeViewSet, DetailCommandeViewSet
from .views import NotificationViewSet

from .views import ProduitViewSet, ImageProduitViewSet, SpecificationProduitViewSet, upload_image
from . import views
from .views import (
    ProduitViewSet, ImageProduitViewSet, SpecificationProduitViewSet, 
    MouvementStockViewSet, CategorieViewSet, NotificationViewSet,
     upload_image
)

router = DefaultRouter()
router.register(r'produits', ProduitViewSet, basename='produit')
router.register(r'specifications', SpecificationProduitViewSet, basename='specification')
router.register(r'mouvements_stock', MouvementStockViewSet, basename='mouvement_stock')
router.register(r'categories', CategorieViewSet, basename='categorie')

router.register(r'commandes', CommandeViewSet)
router.register(r'detail-commandes', DetailCommandeViewSet)

router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    # path('test/', views.test_api, name='test_api'),
    path('upload-image/', upload_image, name='upload-image'),  # NOUVELLE ROUTE
    path('api/signup/', SignupView.as_view(), name='signup'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/request-password-reset/', RequestPasswordResetView.as_view(), name='request-password-reset'),
    path('api/reset-password/<uuid:token>/', ResetPasswordView.as_view(), name='reset-password'),
    path("api/login/google/", GoogleLoginView.as_view(), name="google-login"),
    path('api/facebook-login/', FacebookLoginView.as_view(), name='facebook-login'),
    path('upload-image/', upload_image, name='upload-image'),
]






    

