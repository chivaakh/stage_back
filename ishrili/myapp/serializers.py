# from rest_framework import serializers
# from .models import (
#     Utilisateur, ImageUtilisateur, DetailsClient, DetailsCommercant,
#     Categorie, Produit, ImageProduit, SpecificationProduit,
#     Commande, DetailCommande, Avis, Panier, Favori,
#     MouvementStock, JournalAdmin
# )

# class ProduitDetailSerializer(serializers.ModelSerializer):
#     image_principale = serializers.SerializerMethodField()
#     prix = serializers.SerializerMethodField()
#     prix_promo = serializers.SerializerMethodField()
#     en_stock = serializers.SerializerMethodField()

#     class Meta:
#         model = Produit
#         fields = ['id', 'nom', 'description', 'image_principale', 'prix', 'prix_promo', 'en_stock']

#     def get_image_principale(self, obj):
#         image = obj.imageproduit_set.filter(est_principale=True).first()
#         return image.url_image if image else None

#     def get_prix(self, obj):
#         spec = obj.specificationproduit_set.filter(est_defaut=True).first()
#         return spec.prix if spec else None

#     def get_prix_promo(self, obj):
#         spec = obj.specificationproduit_set.filter(est_defaut=True).first()
#         return spec.prix_promo if spec and spec.prix_promo else None

#     def get_en_stock(self, obj):
#         spec = obj.specificationproduit_set.filter(est_defaut=True).first()
#         return spec.quantite_stock > 0 if spec else False


# class ImageUtilisateurSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ImageUtilisateur
#         fields = '__all__'


# class UtilisateurSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Utilisateur
#         fields = ['id', 'email', 'telephone', 'date_inscription', 'derniere_connexion', 'est_actif', 'role']


# class DetailsClientSerializer(serializers.ModelSerializer):
#     utilisateur = UtilisateurSerializer()
#     photo_profil = ImageUtilisateurSerializer(allow_null=True)

#     class Meta:
#         model = DetailsClient
#         fields = '__all__'


# class DetailsCommercantSerializer(serializers.ModelSerializer):
#     utilisateur = UtilisateurSerializer()
#     logo = ImageUtilisateurSerializer(allow_null=True)

#     class Meta:
#         model = DetailsCommercant
#         fields = '__all__'


# class CategorieSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Categorie
#         fields = '__all__'


# class ProduitSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Produit
#         fields = '__all__'


# class ImageProduitSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ImageProduit
#         fields = '__all__'


# class SpecificationProduitSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SpecificationProduit
#         fields = '__all__'


# class CommandeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Commande
#         fields = '__all__'


# class DetailCommandeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DetailCommande
#         fields = '__all__'


# class AvisSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Avis
#         fields = '__all__'


# class PanierSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Panier
#         fields = '__all__'


# class FavoriSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Favori
#         fields = '__all__'


# class MouvementStockSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = MouvementStock
#         fields = '__all__'


# class JournalAdminSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = JournalAdmin
#         fields = '__all__'
