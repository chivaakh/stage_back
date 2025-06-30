# from rest_framework import serializers/
# from .models import Produit, ImageProduit, SpecificationProduit, 

# myapp/serializers_client.py - Serializers spécifiques aux clients

from rest_framework import serializers
from .models import (
    Produit, ImageProduit, SpecificationProduit, Categorie,
    Panier, Favori, Commande, DetailCommande, Avis,
    DetailsClient, Utilisateur, TrackingCommande
)

class ClientCategorieSerializer(serializers.ModelSerializer):
    """Serializer pour les catégories côté client"""
    nombre_produits = serializers.SerializerMethodField()
    
    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'description', 'nombre_produits']
    
    def get_nombre_produits(self, obj):
        return obj.produit_set.count()

class ClientImageProduitSerializer(serializers.ModelSerializer):
    """Serializer pour les images produit côté client"""
    class Meta:
        model = ImageProduit
        fields = ['id', 'url_image', 'est_principale', 'ordre']

class ClientSpecificationProduitSerializer(serializers.ModelSerializer):
    """Serializer pour les spécifications produit côté client"""
    prix_affichage = serializers.SerializerMethodField()
    en_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = SpecificationProduit
        fields = [
            'id', 'nom', 'description', 'prix', 'prix_promo',
            'quantite_stock', 'est_defaut', 'reference_specification',
            'prix_affichage', 'en_stock'
        ]
    
    def get_prix_affichage(self, obj):
        return obj.prix_promo if obj.prix_promo else obj.prix
    
    def get_en_stock(self, obj):
        return obj.quantite_stock > 0

class ClientProduitSerializer(serializers.ModelSerializer):
    """Serializer pour les produits côté client avec toutes les infos nécessaires"""
    images = ClientImageProduitSerializer(source='imageproduit_set', many=True, read_only=True)
    specifications = ClientSpecificationProduitSerializer(source='specificationproduit_set', many=True, read_only=True)
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    commercant_nom = serializers.CharField(source='commercant.nom_boutique', read_only=True)
    prix_min = serializers.SerializerMethodField()
    prix_max = serializers.SerializerMethodField()
    image_principale = serializers.SerializerMethodField()
    note_moyenne = serializers.SerializerMethodField()
    nombre_avis = serializers.SerializerMethodField()
    
    class Meta:
        model = Produit
        fields = [
            'id', 'reference', 'nom', 'description', 'categorie_nom',
            'commercant_nom', 'images', 'specifications', 'prix_min',
            'prix_max', 'image_principale', 'note_moyenne', 'nombre_avis'
        ]
    
    def get_prix_min(self, obj):
        specs = obj.specificationproduit_set.all()
        if not specs:
            return 0
        return min(spec.prix_promo or spec.prix for spec in specs)
    
    def get_prix_max(self, obj):
        specs = obj.specificationproduit_set.all()
        if not specs:
            return 0
        return max(spec.prix_promo or spec.prix for spec in specs)
    
    def get_image_principale(self, obj):
        image_principale = obj.imageproduit_set.filter(est_principale=True).first()
        if image_principale:
            return image_principale.url_image
        premiere_image = obj.imageproduit_set.first()
        return premiere_image.url_image if premiere_image else None
    
    def get_note_moyenne(self, obj):
        avis = obj.avis_set.all()
        if not avis:
            return 0
        return sum(avis_item.note for avis_item in avis) / len(avis)
    
    def get_nombre_avis(self, obj):
        return obj.avis_set.count()

class PanierSerializer(serializers.ModelSerializer):
    """Serializer pour le panier"""
    produit = serializers.SerializerMethodField()
    specification_details = ClientSpecificationProduitSerializer(source='specification', read_only=True)
    sous_total = serializers.SerializerMethodField()
    
    class Meta:
        model = Panier
        fields = [
            'id', 'quantite', 'date_ajout', 'produit',
            'specification_details', 'sous_total'
        ]
    
    def get_produit(self, obj):
        return {
            'id': obj.specification.produit.id,
            'nom': obj.specification.produit.nom,
            'image_principale': self._get_image_principale(obj.specification.produit)
        }
    
    def _get_image_principale(self, produit):
        image = produit.imageproduit_set.filter(est_principale=True).first()
        return image.url_image if image else None
    
    def get_sous_total(self, obj):
        prix = obj.specification.prix_promo or obj.specification.prix
        return prix * obj.quantite

class PanierCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer/modifier un article dans le panier"""
    class Meta:
        model = Panier
        fields = ['specification', 'quantite']
    
    def validate_quantite(self, value):
        if value <= 0:
            raise serializers.ValidationError("La quantité doit être positive")
        return value
    
    def validate(self, data):
        specification = data['specification']
        quantite = data['quantite']
        
        if specification.quantite_stock < quantite:
            raise serializers.ValidationError(
                f"Stock insuffisant. Disponible: {specification.quantite_stock}"
            )
        return data

class FavoriSerializer(serializers.ModelSerializer):
    """Serializer pour les favoris"""
    produit = ClientProduitSerializer(read_only=True)
    
    class Meta:
        model = Favori
        fields = ['id', 'produit', 'date_ajout']

class AvisSerializer(serializers.ModelSerializer):
    """Serializer pour les avis"""
    client_nom = serializers.SerializerMethodField()
    
    class Meta:
        model = Avis
        fields = [
            'id', 'note', 'commentaire', 'date_creation', 'client_nom'
        ]
        read_only_fields = ['date_creation']
    
    def get_client_nom(self, obj):
        return f"{obj.client.prenom} {obj.client.nom[0]}."

class AvisCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un avis"""
    class Meta:
        model = Avis
        fields = ['produit', 'note', 'commentaire']
    
    def validate_note(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("La note doit être entre 1 et 5")
        return value

class ClientCommandeSerializer(serializers.ModelSerializer):
    """Serializer pour les commandes côté client"""
    details = serializers.SerializerMethodField()
    statut_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Commande
        fields = [
            'id', 'date_commande', 'montant_total', 'statut',
            'statut_display', 'details'
        ]
    
    def get_details(self, obj):
        details = obj.detailcommande_set.all()
        return [{
            'produit_nom': detail.specification.produit.nom,
            'specification_nom': detail.specification.nom,
            'quantite': detail.quantite,
            'prix_unitaire': detail.prix_unitaire,
            'sous_total': detail.quantite * detail.prix_unitaire
        } for detail in details]
    
    def get_statut_display(self, obj):
        statuts = {
            'en_attente': 'En attente',
            'confirmee': 'Confirmée',
            'en_preparation': 'En préparation',
            'expediee': 'Expédiée',
            'livree': 'Livrée',
            'annulee': 'Annulée'
        }
        return statuts.get(obj.statut, obj.statut)

class CommandeCreateSerializer(serializers.Serializer):
    """Serializer pour créer une commande depuis le panier"""
    adresse_livraison = serializers.CharField(max_length=500)
    
    def validate(self, data):
        # Récupérer le client depuis le contexte
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            raise serializers.ValidationError("Utilisateur non authentifié")
        
        # Vérifier que le panier n'est pas vide
        try:
            client = request.user.detailsclient
            panier_items = Panier.objects.filter(client=client)
            if not panier_items.exists():
                raise serializers.ValidationError("Le panier est vide")
        except:
            raise serializers.ValidationError("Client non trouvé")
        
        return data

class DetailsClientSerializer(serializers.ModelSerializer):
    """Serializer pour les détails du client"""
    email = serializers.CharField(source='utilisateur.email', read_only=True)
    telephone = serializers.CharField(source='utilisateur.telephone', read_only=True)
    
    class Meta:
        model = DetailsClient
        fields = [
            'nom', 'prenom', 'adresse', 'ville', 'code_postal',
            'pays', 'email', 'telephone'
        ]


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


class TrackingCommandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingCommande  # ✅ Référence correcte au modèle
        fields = ['ancien_statut', 'nouveau_statut', 'date_modification']


class CommandeSerializer(serializers.ModelSerializer):
    client_nom = serializers.SerializerMethodField()
    client_adresse = serializers.SerializerMethodField()
    client_ville = serializers.SerializerMethodField()
    client_pays = serializers.SerializerMethodField()
    details = DetailCommandeSerializer(source='detailcommande_set', many=True)
    tracking_history = TrackingCommandeSerializer(many=True, read_only=True)

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



    # ... gardez vos méthodes existantes get_client_nom, etc.
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
