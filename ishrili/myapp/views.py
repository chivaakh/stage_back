from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Produit
from .serializers import ProduitSerializer

class ProduitViewSet(viewsets.ModelViewSet):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer
    permission_classes = []
    
    def perform_create(self, serializer):
        # Temporaire : associer au premier commerçant trouvé
        from .models import DetailsCommercant
        commercant = DetailsCommercant.objects.first()
        serializer.save(commercant=commercant)


# from rest_framework import viewsets
# from .models import (
#     Utilisateur, ImageUtilisateur, DetailsClient, DetailsCommercant,
#     Categorie, Produit, ImageProduit, SpecificationProduit,
#     Commande, DetailCommande, Avis, Panier, Favori,
#     MouvementStock, JournalAdmin
# )
# from .serializers import (
#     UtilisateurSerializer, ImageUtilisateurSerializer, DetailsClientSerializer, DetailsCommercantSerializer,
#     CategorieSerializer, ProduitSerializer, ImageProduitSerializer, SpecificationProduitSerializer,
#     CommandeSerializer, DetailCommandeSerializer, AvisSerializer, PanierSerializer, FavoriSerializer,
#     MouvementStockSerializer, JournalAdminSerializer
# )

# class UtilisateurViewSet(viewsets.ModelViewSet):
#     queryset = Utilisateur.objects.all()
#     serializer_class = UtilisateurSerializer

# class ImageUtilisateurViewSet(viewsets.ModelViewSet):
#     queryset = ImageUtilisateur.objects.all()
#     serializer_class = ImageUtilisateurSerializer

# class DetailsClientViewSet(viewsets.ModelViewSet):
#     queryset = DetailsClient.objects.all()
#     serializer_class = DetailsClientSerializer

# class DetailsCommercantViewSet(viewsets.ModelViewSet):
#     queryset = DetailsCommercant.objects.all()
#     serializer_class = DetailsCommercantSerializer

# class CategorieViewSet(viewsets.ModelViewSet):
#     queryset = Categorie.objects.all()
#     serializer_class = CategorieSerializer



# from rest_framework.permissions import AllowAny, IsAuthenticated
# from rest_framework.viewsets import ModelViewSet
# from .models import Produit
# from .serializers import ProduitSerializer, ProduitDetailSerializer

# class ProduitViewSet(ModelViewSet):
#     queryset = Produit.objects.all()

#     def get_permissions(self):
#         if self.action in ['list', 'retrieve']:
#             return [AllowAny()]
#         return [IsAuthenticated()]

#     def get_serializer_class(self):
#         if self.action in ['list', 'retrieve']:
#             return ProduitDetailSerializer
#         return ProduitSerializer


# class ImageProduitViewSet(viewsets.ModelViewSet):
#     queryset = ImageProduit.objects.all()
#     serializer_class = ImageProduitSerializer

# class SpecificationProduitViewSet(viewsets.ModelViewSet):
#     queryset = SpecificationProduit.objects.all()
#     serializer_class = SpecificationProduitSerializer

# class CommandeViewSet(viewsets.ModelViewSet):
#     queryset = Commande.objects.all()
#     serializer_class = CommandeSerializer

# class DetailCommandeViewSet(viewsets.ModelViewSet):
#     queryset = DetailCommande.objects.all()
#     serializer_class = DetailCommandeSerializer

# class AvisViewSet(viewsets.ModelViewSet):
#     queryset = Avis.objects.all()
#     serializer_class = AvisSerializer

# class PanierViewSet(viewsets.ModelViewSet):
#     queryset = Panier.objects.all()
#     serializer_class = PanierSerializer

# class FavoriViewSet(viewsets.ModelViewSet):
#     queryset = Favori.objects.all()
#     serializer_class = FavoriSerializer

# class MouvementStockViewSet(viewsets.ModelViewSet):
#     queryset = MouvementStock.objects.all()
#     serializer_class = MouvementStockSerializer

# class JournalAdminViewSet(viewsets.ModelViewSet):
#     queryset = JournalAdmin.objects.all()
#     serializer_class = JournalAdminSerializer

