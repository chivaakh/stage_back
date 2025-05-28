from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets
from .models import (
    Utilisateur, ImageUtilisateur, DetailsClient, DetailsCommercant,
    Categorie, Produit, ImageProduit, SpecificationProduit,
    Commande, DetailCommande, Avis, Panier, Favori,
    MouvementStock, JournalAdmin
)
from .serializers import (
    UtilisateurSerializer, ImageUtilisateurSerializer, DetailsClientSerializer, DetailsCommercantSerializer,
    CategorieSerializer, ProduitSerializer, ImageProduitSerializer, SpecificationProduitSerializer,
    CommandeSerializer, DetailCommandeSerializer, AvisSerializer, PanierSerializer, FavoriSerializer,
    MouvementStockSerializer, JournalAdminSerializer
)

class UtilisateurViewSet(viewsets.ModelViewSet):
    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurSerializer

class ImageUtilisateurViewSet(viewsets.ModelViewSet):
    queryset = ImageUtilisateur.objects.all()
    serializer_class = ImageUtilisateurSerializer

class DetailsClientViewSet(viewsets.ModelViewSet):
    queryset = DetailsClient.objects.all()
    serializer_class = DetailsClientSerializer

class DetailsCommercantViewSet(viewsets.ModelViewSet):
    queryset = DetailsCommercant.objects.all()
    serializer_class = DetailsCommercantSerializer

class CategorieViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer

class ProduitViewSet(viewsets.ModelViewSet):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer

class ImageProduitViewSet(viewsets.ModelViewSet):
    queryset = ImageProduit.objects.all()
    serializer_class = ImageProduitSerializer

class SpecificationProduitViewSet(viewsets.ModelViewSet):
    queryset = SpecificationProduit.objects.all()
    serializer_class = SpecificationProduitSerializer

class CommandeViewSet(viewsets.ModelViewSet):
    queryset = Commande.objects.all()
    serializer_class = CommandeSerializer

class DetailCommandeViewSet(viewsets.ModelViewSet):
    queryset = DetailCommande.objects.all()
    serializer_class = DetailCommandeSerializer

class AvisViewSet(viewsets.ModelViewSet):
    queryset = Avis.objects.all()
    serializer_class = AvisSerializer

class PanierViewSet(viewsets.ModelViewSet):
    queryset = Panier.objects.all()
    serializer_class = PanierSerializer

class FavoriViewSet(viewsets.ModelViewSet):
    queryset = Favori.objects.all()
    serializer_class = FavoriSerializer

class MouvementStockViewSet(viewsets.ModelViewSet):
    queryset = MouvementStock.objects.all()
    serializer_class = MouvementStockSerializer

class JournalAdminViewSet(viewsets.ModelViewSet):
    queryset = JournalAdmin.objects.all()
    serializer_class = JournalAdminSerializer


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])  # Permet l'accès sans authentification
def test_api(request):
    return Response({
        'message': 'Connexion Django-React réussie !',
        'status': 'OK',
        'timestamp': '2025-05-28',
        'data': {
            'server': 'Django 4.2.20',
            'client': 'React',
            'test': True
        }
    })