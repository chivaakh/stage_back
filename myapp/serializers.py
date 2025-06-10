from rest_framework import serializers
from .models import Produit, ImageProduit, SpecificationProduit, Utilisateur
from django.contrib.auth.hashers import make_password


class SignupSerializer(serializers.ModelSerializer):
    prenom = serializers.CharField(write_only=True, required=True)
    nom = serializers.CharField(required=False, allow_blank=True)
    mot_de_passe = serializers.CharField(write_only=True, required=True, min_length=6)
    email = serializers.EmailField(required=False, allow_blank=True)
    telephone = serializers.CharField(required=True)

    class Meta:
        model = Utilisateur
        fields = ['nom', 'prenom', 'email', 'telephone', 'mot_de_passe']

    def validate(self, data):
        if not data.get('email') and not data.get('telephone'):
            raise serializers.ValidationError("Email ou téléphone doit être renseigné.")
        return data

    def create(self, validated_data):
        # Hash du mot de passe
        mot_de_passe = validated_data.pop('mot_de_passe')
        utilisateur = Utilisateur(**validated_data)
        utilisateur.mot_de_passe = make_password(mot_de_passe)
        utilisateur.type_utilisateur = 'vendeur'  # Role par défaut
        utilisateur.save()
        return utilisateur



class LoginSerializer(serializers.Serializer):
    identifiant = serializers.CharField(required=True)  # email ou téléphone
    mot_de_passe = serializers.CharField(required=True, write_only=True)




class ImageProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageProduit
        fields = ['id', 'produit', 'url_image', 'est_principale', 'ordre', 'date_ajout']
        read_only_fields = ['date_ajout']

class SpecificationProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecificationProduit
        fields = [
            'id', 'produit', 'nom', 'description', 'prix', 'prix_promo', 
            'quantite_stock', 'est_defaut', 'reference_specification'
        ]
from .models import Produit
from .models import SpecificationProduit, MouvementStock



class ProduitSerializer(serializers.ModelSerializer):
    # ✅ CORRECTION : Utiliser le bon nom de relation
    images = ImageProduitSerializer(many=True, read_only=True, source='imageproduit_set')
    specifications = SpecificationProduitSerializer(many=True, read_only=True, source='specificationproduit_set')
    
    class Meta:
        model = Produit
        fields = [
            'id', 'nom', 'description', 'reference', 'commercant', 'categorie',
            'images', 'specifications'
        ]
        extra_kwargs = {
            'commercant': {'required': False, 'allow_null': True},
            'categorie': {'required': False, 'allow_null': True}
        }

    def to_representation(self, instance):
        """Personnaliser la représentation"""
        data = super().to_representation(instance)
        
        # Ajouter des infos supplémentaires
        if instance.commercant:
            data['commercant_info'] = {
                'id': instance.commercant.id,
                'nom_boutique': instance.commercant.nom_boutique,
                'ville': instance.commercant.ville
            }
        
        # Calculer le prix min/max des spécifications
        specs = instance.specificationproduit_set.all()
        if specs:
            prix_list = [spec.prix_promo if spec.prix_promo else spec.prix for spec in specs]
            data['prix_min'] = min(prix_list) if prix_list else None
            data['prix_max'] = max(prix_list) if prix_list else None
        
        # Image principale
        images = instance.imageproduit_set.filter(est_principale=True).first()
        if not images:
            images = instance.imageproduit_set.first()
        data['image_principale'] = images.url_image if images else None
        
        return data




class SpecificationProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecificationProduit
        fields = ['id', 'produit', 'nom', 'quantite_stock', 'prix', 'prix_promo']
        read_only_fields = ['produit', 'nom', 'prix', 'prix_promo']  # On ne modifie que la quantité ici

class MouvementStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = MouvementStock
        fields = ['id', 'specification', 'quantite', 'type_mouvement', 'reference_document', 'commentaire', 'date_mouvement']
        read_only_fields = ['date_mouvement']

    def validate(self, data):
        if data['quantite'] <= 0:
            raise serializers.ValidationError("La quantité doit être positive")
        if data['type_mouvement'] not in ['entree', 'sortie']:
            raise serializers.ValidationError("Le type de mouvement doit être 'entree' ou 'sortie'")
        return data





















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
