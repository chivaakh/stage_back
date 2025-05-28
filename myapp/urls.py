from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .import views
from .views import ProduitViewSet

router = DefaultRouter()
router.register(r'produits', ProduitViewSet, basename='produit')

urlpatterns = [
    path('', include(router.urls)),
    path('test/', views.test_api, name='test_api'),
]
