# myapp/urls.py - Imports corrigés
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdminBoutiquesViewSet, AdminNotificationViewSet, CampaignViewSet, CreerProfilVendeurView, ProduitViewSet, ImageProduitViewSet, SignupView, SpecificationProduitViewSet,
    MouvementStockViewSet, CategorieViewSet, NotificationViewSet,
    ClientProduitViewSet, ClientCategorieViewSet, 
    PanierViewSet,
    FavoriViewSet, AvisViewSet, ClientCommandeViewSet, ClientProfilViewSet,
    CommandeViewSet, DetailCommandeViewSet,
    # API Views - Supprimé SignupView qui n'existe pas
    LoginView,
    RequestPasswordResetView, ResetPasswordView,
    GoogleLoginView, FacebookLoginView, SystemAlertViewSet, VendeurInfoView,AdminUsersViewSet, admin_boutiques_stats, admin_stats, admin_recent_activity,ModerationProduitViewSet, SignalementProduitViewSet,
    EvaluationQualiteViewSet, CritereQualiteViewSet,
    DashboardModerationView,
    # Functions
    upload_image, debug_products, debug_images_complete,
)



# Router configuration
router = DefaultRouter()

# Frontend client routes
router.register(r'client/produits', ClientProduitViewSet, basename='client-produits')
router.register(r'client/categories', ClientCategorieViewSet, basename='client-categories')
router.register(r'client/panier', PanierViewSet, basename='panier')
router.register(r'client/favoris', FavoriViewSet, basename='favoris')
router.register(r'client/avis', AvisViewSet, basename='avis')
router.register(r'client/commandes', ClientCommandeViewSet, basename='client-commandes')
router.register(r'client/profil', ClientProfilViewSet, basename='client-profil')

# admin 
router.register(r'admin/users', AdminUsersViewSet, basename='admin-users')
router.register(r'admin/boutiques', AdminBoutiquesViewSet, basename='admin-boutiques')
router.register(r'admin/moderation/produits', ModerationProduitViewSet, basename='moderation-produits')
router.register(r'admin/signalements', SignalementProduitViewSet, basename='signalements')
router.register(r'admin/evaluations-qualite', EvaluationQualiteViewSet, basename='evaluations-qualite')
router.register(r'admin/criteres-qualite', CritereQualiteViewSet, basename='criteres-qualite')
# dayertu wethi9a
router.register(r'client/signalements', SignalementProduitViewSet, basename='client-signalements')
# notification admin 
router.register(r'admin/notifications', AdminNotificationViewSet, basename='admin-notifications')
router.register(r'campaigns', CampaignViewSet, basename='campaigns')
router.register(r'alerts', SystemAlertViewSet, basename='alerts')




# Admin or shared routes
router.register(r'produits', ProduitViewSet, basename='produit')
router.register(r'images', ImageProduitViewSet, basename='image')
router.register(r'specifications', SpecificationProduitViewSet, basename='specification')
router.register(r'mouvements_stock', MouvementStockViewSet, basename='mouvement_stock')
router.register(r'categories', CategorieViewSet, basename='categorie')
router.register(r'commandes', CommandeViewSet, basename='commandes')  #  important pour /commandes/<id>/tracking/
router.register(r'detail-commandes', DetailCommandeViewSet)
router.register(r'notifications', NotificationViewSet, basename='notification')
urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    path('upload-image/', upload_image, name='upload-image'),
    path('api/signup/', SignupView.as_view(), name='signup'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/request-password-reset/', RequestPasswordResetView.as_view(), name='request-password-reset'),
    path('api/reset-password/<uuid:token>/', ResetPasswordView.as_view(), name='reset-password'),
    path("api/login/google/", GoogleLoginView.as_view(), name="google-login"),
    path('api/facebook-login/', FacebookLoginView.as_view(), name='facebook-login'),
    path('api/profil-vendeur/', CreerProfilVendeurView.as_view(), name='profil_vendeur'),
    path('api/vendeur-info/', VendeurInfoView.as_view(), name='vendeur_info'),
    path('upload-image/', upload_image, name='upload-image'),

# admin
    path('api/admin/stats/', admin_stats, name='admin-stats'),
    path('api/admin/activity/', admin_recent_activity, name='admin-activity'),
    path('api/admin/boutiques/stats/', admin_boutiques_stats, name='admin-boutiques-stats'),
    path('admin/dashboard-moderation/', DashboardModerationView.as_view(), name='dashboard-moderation'),

    # Utility URLs
    path('upload-image/', upload_image, name='upload-image'),
    path('debug-products/', debug_products, name='debug-products'),
    path('debug-images/', debug_images_complete, name='debug-images'),

]
