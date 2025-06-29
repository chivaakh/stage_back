# myapp/urls.py - Imports corrigés
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # ViewSets
    ProduitViewSet, ImageProduitViewSet, SpecificationProduitViewSet,
    MouvementStockViewSet, CategorieViewSet, CommandeViewSet,
    DetailCommandeViewSet, NotificationViewSet,
    # API Views - ✅ Supprimé SignupView qui n'existe pas
    SignupWithDetailsView, LoginView,
    RequestPasswordResetView, ResetPasswordView,
    GoogleLoginView, FacebookLoginView,
    # Functions
    upload_image, debug_products, debug_images_complete,
)

# Router configuration
router = DefaultRouter()
router.register(r'produits', ProduitViewSet, basename='produit')
router.register(r'images', ImageProduitViewSet, basename='image')
router.register(r'specifications', SpecificationProduitViewSet, basename='specification')
router.register(r'mouvements_stock', MouvementStockViewSet, basename='mouvement_stock')
router.register(r'categories', CategorieViewSet, basename='categorie')
router.register(r'commandes', CommandeViewSet, basename='commande')
router.register(r'detail-commandes', DetailCommandeViewSet, basename='detail-commande')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Auth URLs - ✅ Supprimé la route 'api/signup/' qui utilisait SignupView
    path('api/signup-with-details/', SignupWithDetailsView.as_view(), name='signup-with-details'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/request-password-reset/', RequestPasswordResetView.as_view(), name='request-password-reset'),
    path('api/reset-password/<uuid:token>/', ResetPasswordView.as_view(), name='reset-password'),
    path('api/login/google/', GoogleLoginView.as_view(), name='google-login'),
    path('api/facebook-login/', FacebookLoginView.as_view(), name='facebook-login'),
    
    # Utility URLs
    path('upload-image/', upload_image, name='upload-image'),
    path('debug-products/', debug_products, name='debug-products'),
    path('debug-images/', debug_images_complete, name='debug-images'),
]