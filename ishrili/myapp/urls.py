from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# Tu peux décommenter les ViewSet si besoin
# router.register(r'utilisateurs', views.UtilisateurViewSet)

urlpatterns = [
    path('test/', views.test_connection, name='test'),  # 👈 Ici est ta route API
    path('', include(router.urls)),
]
