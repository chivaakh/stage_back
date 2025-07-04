from rest_framework import serializers
from .models import Produit, ImageProduit, SpecificationProduit, Utilisateur, ProfilVendeur
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
        request = self.context.get('request')
        type_utilisateur = request.data.get('type_utilisateur')

        if type_utilisateur not in ['client', 'vendeur']:
            raise serializers.ValidationError("Le type d'utilisateur est requis et doit être 'client' ou 'vendeur'.")

        mot_de_passe = validated_data.pop('mot_de_passe')
        utilisateur = Utilisateur(**validated_data)
        utilisateur.mot_de_passe = make_password(mot_de_passe)
        utilisateur.type_utilisateur = type_utilisateur
        utilisateur.save()
        return utilisateur




class LoginSerializer(serializers.Serializer):
    identifiant = serializers.CharField(required=True)  # email ou téléphone
    mot_de_passe = serializers.CharField(required=True, write_only=True)




# Version alternative si le problème persiste - dans serializers.py

class ProfilVendeurSerializer(serializers.ModelSerializer):
    # Exclure utilisateur des champs gérés automatiquement
    utilisateur = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = ProfilVendeur
        fields = [
            'id',
            'utilisateur',
            'nom_boutique', 
            'description', 
            'adresse', 
            'ville', 
            'telephone_professionnel', 
            'logo',
            'est_approuve', 
            'total_ventes', 
            'evaluation', 
            'date_creation', 
            'date_modification'
        ]
        read_only_fields = ['id_profil_vendeur', 'utilisateur', 'est_approuve', 'total_ventes', 'evaluation', 'date_creation', 'date_modification']

    def create(self, validated_data):
        # L'utilisateur sera passé via serializer.save(utilisateur=utilisateur)
        return ProfilVendeur.objects.create(**validated_data)












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





from rest_framework import serializers
from .models import Categorie

class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'description']

from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    produit = serializers.StringRelatedField(read_only=True)  # Affiche le nom du produit

    class Meta:
        model = Notification
        fields = ['id', 'produit', 'date_notification', 'message', 'est_lue']
        read_only_fields = ['date_notification', 'produit', 'message']

from rest_framework import serializers
from .models import Commande, DetailCommande

class DetailCommandeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)  # permet l’update via id
    specification = serializers.PrimaryKeyRelatedField(queryset=SpecificationProduit.objects.all())
    specification_nom = serializers.CharField(source='specification.nom', read_only=True)
    class Meta:
        model = DetailCommande
        fields = ['id', 'quantite', 'prix_unitaire', 'specification', 'specification_nom']

class CommandeSerializer(serializers.ModelSerializer):
    client_nom = serializers.SerializerMethodField()
    client_adresse = serializers.SerializerMethodField()
    client_ville = serializers.SerializerMethodField()
    client_pays = serializers.SerializerMethodField()
    details = DetailCommandeSerializer(source='detailcommande_set', many=True)
    
    class Meta:
        model = Commande
        fields = '__all__'

    def get_client_nom(self, obj):
        try:
            return obj.client.nom
        except:
            return "-"

    def get_client_adresse(self, obj):
        try:
            return obj.client.adresse
        except:
            return "-"

    def get_client_ville(self, obj):
        try:
            return obj.client.ville
        except:
            return "-"

    def get_client_pays(self, obj):
        try:
            return obj.client.pays
        except:
            return "-"

    def update(self, instance, validated_data):
        details_data = validated_data.pop('detailcommande_set', [])

        # Met à jour les champs simples
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Gère les détails imbriqués : suppression des détails non présents
        detail_ids = [item.get('id') for item in details_data if 'id' in item]
        DetailCommande.objects.filter(commande=instance).exclude(id__in=detail_ids).delete()
# Ajouter ce serializer à votre serializers.py existant

        # Mise à jour ou création des détails
        for detail_data in details_data:
            detail_id = detail_data.get('id', None)
            if detail_id:
                detail = DetailCommande.objects.get(id=detail_id, commande=instance)
                for attr, value in detail_data.items():
                    setattr(detail, attr, value)
                detail.save()
            else:
                DetailCommande.objects.create(commande=instance, **detail_data)

        return instance
    
    
