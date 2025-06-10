# myapp/urls.py - AJOUTER cette route
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .import views
from .views import ProduitViewSet
from .views import ProduitViewSet, ImageProduitViewSet, SpecificationProduitViewSet
from .views import ProduitViewSet,SpecificationProduitViewSet, MouvementStockViewSet


from .views import ProduitViewSet, ImageProduitViewSet, SpecificationProduitViewSet, upload_image

router = DefaultRouter()
router.register(r'produits', ProduitViewSet, basename='produit')
router.register(r'specifications', SpecificationProduitViewSet, basename='specification')
router.register(r'mouvements_stock', MouvementStockViewSet, basename='mouvement_stock')

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


    

