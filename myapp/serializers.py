from rest_framework import serializers
from .models import (
    Utilisateur, ImageUtilisateur, DetailsClient, DetailsCommercant,
    Categorie, Produit, ImageProduit, SpecificationProduit,
    Commande, DetailCommande, Avis, Panier, Favori,
    MouvementStock, JournalAdmin
)


class ImageUtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageUtilisateur
        fields = '__all__'


class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ['id', 'email', 'telephone', 'date_inscription', 'derniere_connexion', 'est_actif', 'role']


class DetailsClientSerializer(serializers.ModelSerializer):
    utilisateur = UtilisateurSerializer()
    photo_profil = ImageUtilisateurSerializer(allow_null=True)

    class Meta:
        model = DetailsClient
        fields = '__all__'


class DetailsCommercantSerializer(serializers.ModelSerializer):
    utilisateur = UtilisateurSerializer()
    logo = ImageUtilisateurSerializer(allow_null=True)

    class Meta:
        model = DetailsCommercant
        fields = '__all__'


class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = '__all__'


class ProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = '__all__'


class ImageProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageProduit
        fields = '__all__'


class SpecificationProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecificationProduit
        fields = '__all__'


class CommandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commande
        fields = '__all__'


class DetailCommandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetailCommande
        fields = '__all__'


class AvisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avis
        fields = '__all__'


class PanierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Panier
        fields = '__all__'


class FavoriSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favori
        fields = '__all__'


class MouvementStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = MouvementStock
        fields = '__all__'


class JournalAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalAdmin
        fields = '__all__'
