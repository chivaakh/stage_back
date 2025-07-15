# serializers.py - VERSION CORRIGÉE AVEC BON ORDRE
import logging
logger = logging.getLogger(__name__)
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import (
    Campaign, Produit, ImageProduit, SpecificationProduit, SystemAlert, 
    Utilisateur, ProfilVendeur, DetailsClient, DetailsCommercant,
    Categorie, Notification, Commande, DetailCommande, 
    TrackingCommande, Avis, Panier, Favori, MouvementStock
)
from . import models
from dateutil import parser
from django.utils import timezone

# ===== 1. SERIALIZERS DE BASE (D'ABORD LES PLUS SIMPLES) =====

class CategorieSerializer(serializers.ModelSerializer):
    """Serializer pour les catégories - DÉFINI EN PREMIER"""
    nombre_produits = serializers.SerializerMethodField()
    
    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'description', 'nombre_produits']
    
    def get_nombre_produits(self, obj):
        """Compter le nombre de produits dans cette catégorie"""
        try:
            return obj.produit_set.count()
        except:
            return 0

class ImageProduitSerializer(serializers.ModelSerializer):
    """Serializer pour les images de produits"""
    produit_nom = serializers.CharField(source='produit.nom', read_only=True)
    
    class Meta:
        model = ImageProduit
        fields = [
            'id', 'produit', 'url_image', 'est_principale', 'ordre', 
            'date_ajout', 'produit_nom'
        ]
        read_only_fields = ['date_ajout']

class SpecificationProduitSerializer(serializers.ModelSerializer):
    """Serializer pour les spécifications"""
    prix_final = serializers.SerializerMethodField()
    statut_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = SpecificationProduit
        fields = [
            'id', 'produit', 'nom', 'description', 'prix', 'prix_promo', 
            'quantite_stock', 'est_defaut', 'reference_specification',
            'prix_final', 'statut_stock'
        ]
    
    def get_prix_final(self, obj):
        """Prix final (promo si disponible, sinon prix normal)"""
        try:
            return float(obj.prix_promo if obj.prix_promo else obj.prix)
        except:
            return float(obj.prix) if obj.prix else 0
    
    def get_statut_stock(self, obj):
        """Statut du stock"""
        try:
            if obj.quantite_stock <= 0:
                return "rupture"
            elif obj.quantite_stock <= 5:
                return "faible"
            elif obj.quantite_stock <= 20:
                return "moyen"
            else:
                return "bon"
        except:
            return "rupture"

# ===== 2. SERIALIZER PRODUIT PRINCIPAL (MAINTENANT QU'ON A CATÉGORIE) =====

# Dans serializers.py - REMPLACER ProduitSerializer par cette version

class ProduitSerializer(serializers.ModelSerializer):
    """Serializer principal pour les produits"""
    images = ImageProduitSerializer(many=True, read_only=True, source='imageproduit_set')
    specifications = SpecificationProduitSerializer(many=True, read_only=True, source='specificationproduit_set')
    
    # Catégorie (existant)
    categorie = CategorieSerializer(read_only=True)
    categorie_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    # ✅ NOUVEAU : Champs vendeur
    vendeur = serializers.StringRelatedField(read_only=True)  # Affichage nom boutique
    vendeur_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    # ✅ NOUVEAU : Informations vendeur en lecture seule
    nom_boutique = serializers.SerializerMethodField()
    ville_boutique = serializers.SerializerMethodField()
    
    # Champs calculés existants
    prix_min = serializers.SerializerMethodField()
    prix_max = serializers.SerializerMethodField()
    stock_total = serializers.SerializerMethodField()
    image_principale = serializers.SerializerMethodField()
    
    # ... vos champs existants ...
    
    # AJOUTS POUR LA MODÉRATION
    statut_moderation_display = serializers.CharField(
        source='get_statut_moderation_display', read_only=True
    )
    moderateur_nom = serializers.SerializerMethodField()
    nombre_signalements_actifs = serializers.SerializerMethodField()
    
    class Meta:
        model = Produit
        fields = [
            # Vos champs existants
            'id', 'nom', 'description', 'reference', 'commercant',
            'categorie', 'categorie_id', 
            'vendeur', 'vendeur_id', 'nom_boutique', 'ville_boutique',  # ✅ NOUVEAU
            'images', 'specifications',
            'prix_min', 'prix_max', 'stock_total', 'image_principale',
            
            # NOUVEAUX CHAMPS DE MODÉRATION
            'est_approuve', 'statut_moderation', 'statut_moderation_display',
            'date_moderation', 'moderateur', 'moderateur_nom',
            'raison_rejet', 'est_visible', 'score_qualite',
            'nombre_signalements_actifs'
        ]
        extra_kwargs = {
            'commercant': {'required': False, 'allow_null': True},
            'vendeur_id': {'required': False, 'allow_null': True},
        }
    
    def get_nom_boutique(self, obj):
        """✅ NOUVEAU : Nom de la boutique du vendeur"""
        try:
            return obj.vendeur.nom_boutique if obj.vendeur else None
        except:
            return None
    
    def get_ville_boutique(self, obj):
        """✅ NOUVEAU : Ville de la boutique"""
        try:
            return obj.vendeur.ville if obj.vendeur else None
        except:
            return None
    
    # Méthodes existantes inchangées
    
    def get_moderateur_nom(self, obj):
        try:
            if obj.moderateur:
                return f"{obj.moderateur.prenom or ''} {obj.moderateur.nom or ''}".strip()
            return None
        except:
            return None
    
    def get_nombre_signalements_actifs(self, obj):
        try:
            return obj.signalements.filter(statut__in=['nouveau', 'en_cours']).count()
        except:
            return 0
    

        
    def get_prix_min(self, obj):
        try:
            specs = obj.specificationproduit_set.all()
            if specs:
                prix_list = [spec.prix_promo if spec.prix_promo else spec.prix for spec in specs]
                return float(min(prix_list)) if prix_list else 0
            return 0
        except:
            return 0
    
    def get_prix_max(self, obj):
        try:
            specs = obj.specificationproduit_set.all()
            if specs:
                prix_list = [spec.prix_promo if spec.prix_promo else spec.prix for spec in specs]
                return float(max(prix_list)) if prix_list else 0
            return 0
        except:
            return 0
    
    def get_stock_total(self, obj):
        try:
            specs = obj.specificationproduit_set.all()
            return sum(spec.quantite_stock for spec in specs)
        except:
            return 0
    
    def get_image_principale(self, obj):
        try:
            image_principale = obj.imageproduit_set.filter(est_principale=True).first()
            if image_principale:
                return {
                    'id': image_principale.id,
                    'url_image': image_principale.url_image,
                    'ordre': image_principale.ordre
                }
            premiere_image = obj.imageproduit_set.first()
            if premiere_image:
                return {
                    'id': premiere_image.id,
                    'url_image': premiere_image.url_image,
                    'ordre': premiere_image.ordre
                }
            return None
        except:
            return None
    
    def create(self, validated_data):
        """✅ MODIFIÉ : Créer un produit avec vendeur et catégorie"""
        categorie_id = validated_data.pop('categorie_id', None)
        vendeur_id = validated_data.pop('vendeur_id', None)  # ✅ NOUVEAU
        
        produit = Produit.objects.create(**validated_data)
        
        # Associer catégorie
        if categorie_id:
            try:
                categorie = Categorie.objects.get(id=categorie_id)
                produit.categorie = categorie
                produit.save()
            except Categorie.DoesNotExist:
                pass
        
        # ✅ NOUVEAU : Associer vendeur (optionnel car fait dans perform_create)
        if vendeur_id:
            try:
                vendeur = ProfilVendeur.objects.get(id=vendeur_id)
                produit.vendeur = vendeur
                produit.save()
            except ProfilVendeur.DoesNotExist:
                pass
        
        return produit
    
    def update(self, instance, validated_data):
        """✅ MODIFIÉ : Mettre à jour avec catégorie et vendeur"""
        categorie_id = validated_data.pop('categorie_id', None)
        vendeur_id = validated_data.pop('vendeur_id', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Catégorie
        if categorie_id is not None:
            try:
                if categorie_id == '' or categorie_id is None:
                    instance.categorie = None
                else:
                    categorie = Categorie.objects.get(id=categorie_id)
                    instance.categorie = categorie
            except Categorie.DoesNotExist:
                pass
        
        # ✅ NOUVEAU : Vendeur (normalement ne devrait pas changer)
        if vendeur_id is not None:
            try:
                if vendeur_id == '' or vendeur_id is None:
                    instance.vendeur = None
                else:
                    vendeur = ProfilVendeur.objects.get(id=vendeur_id)
                    instance.vendeur = vendeur
            except ProfilVendeur.DoesNotExist:
                pass
        
        instance.save()
        return instance

# ===== 3. SERIALIZERS UTILISATEURS =====

class SignupSerializer(serializers.ModelSerializer):
    prenom = serializers.CharField(write_only=True, required=True)
    nom = serializers.CharField(required=False, allow_blank=True)
    mot_de_passe = serializers.CharField(write_only=True, required=True, min_length=6)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    telephone = serializers.CharField(required=True)

    class Meta:
        model = Utilisateur
        fields = ['nom', 'prenom', 'email', 'telephone', 'mot_de_passe']

    def validate(self, data):
        if not data.get('email') and not data.get('telephone'):
            raise serializers.ValidationError("Email ou téléphone doit être renseigné.")
        
        email = data.get('email')
        if email is None or email.strip() == '':
            data['email'] = None
        else:
            data['email'] = email.strip()
            
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        type_utilisateur = request.data.get('type_utilisateur')

        if type_utilisateur not in ['client', 'vendeur']:
            raise serializers.ValidationError("Le type d'utilisateur est requis et doit être 'client' ou 'vendeur'.")

        mot_de_passe = validated_data.pop('mot_de_passe')
        
        if validated_data.get('email') == '':
            validated_data['email'] = None
            
        utilisateur = Utilisateur(**validated_data)
        utilisateur.mot_de_passe = make_password(mot_de_passe)
        utilisateur.type_utilisateur = type_utilisateur
        utilisateur.save()
        return utilisateur

class LoginSerializer(serializers.Serializer):
    identifiant = serializers.CharField(required=True)
    mot_de_passe = serializers.CharField(required=True, write_only=True)

# ===== 4. SERIALIZERS E-COMMERCE =====

class PanierSerializer(serializers.ModelSerializer):
    """Serializer pour afficher le panier"""
    specification_nom = serializers.CharField(source='specification.nom', read_only=True)
    specification_prix = serializers.DecimalField(source='specification.prix', max_digits=10, decimal_places=2, read_only=True)
    specification_prix_promo = serializers.DecimalField(source='specification.prix_promo', max_digits=10, decimal_places=2, read_only=True)
    produit_nom = serializers.CharField(source='specification.produit.nom', read_only=True)
    produit_reference = serializers.CharField(source='specification.produit.reference', read_only=True)
    produit_image = serializers.SerializerMethodField()
    prix_unitaire = serializers.SerializerMethodField()
    prix_total = serializers.SerializerMethodField()
    stock_disponible = serializers.IntegerField(source='specification.quantite_stock', read_only=True)
    
    class Meta:
        model = Panier
        fields = [
            'id', 'specification', 'quantite', 'date_ajout', 'date_modification',
            'specification_nom', 'specification_prix', 'specification_prix_promo',
            'produit_nom', 'produit_reference', 'produit_image', 
            'prix_unitaire', 'prix_total', 'stock_disponible'
        ]
        read_only_fields = ['client', 'date_ajout', 'date_modification']
    
    def get_produit_image(self, obj):
        try:
            image = obj.specification.produit.imageproduit_set.filter(est_principale=True).first()
            if not image:
                image = obj.specification.produit.imageproduit_set.first()
            return image.url_image if image else None
        except:
            return None
    
    def get_prix_unitaire(self, obj):
        try:
            return float(obj.specification.prix_promo or obj.specification.prix)
        except:
            return 0
    
    def get_prix_total(self, obj):
        try:
            prix_unitaire = obj.specification.prix_promo or obj.specification.prix
            return float(prix_unitaire * obj.quantite)
        except:
            return 0
        
class PanierCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer/modifier un article dans le panier"""
    
    class Meta:
        model = Panier
        fields = ['specification', 'quantite']
    
    def validate_quantite(self, value):
        """Valider la quantité"""
        if value <= 0:
            raise serializers.ValidationError("La quantité doit être supérieure à 0")
        return value
    
    def validate_specification(self, value):
        """Vérifier que la spécification existe et a du stock"""
        if not value:
            raise serializers.ValidationError("Spécification requise")
        
        if value.quantite_stock <= 0:
            raise serializers.ValidationError("Produit en rupture de stock")
        
        return value
    
    def validate(self, data):
        """Validation globale"""
        specification = data.get('specification')
        quantite = data.get('quantite')
        
        if specification and quantite:
            if quantite > specification.quantite_stock:
                raise serializers.ValidationError(
                    f"Quantité demandée ({quantite}) supérieure au stock disponible ({specification.quantite_stock})"
                )
        
        return data

class FavoriSerializer(serializers.ModelSerializer):
    """Serializer pour afficher les favoris"""
    produit_nom = serializers.CharField(source='produit.nom', read_only=True)
    produit_description = serializers.CharField(source='produit.description', read_only=True)
    produit_reference = serializers.CharField(source='produit.reference', read_only=True)
    produit_image = serializers.SerializerMethodField()
    prix_min = serializers.SerializerMethodField()
    prix_max = serializers.SerializerMethodField()
    
    class Meta:
        model = Favori
        fields = [
            'id', 'client', 'produit', 'date_ajout',
            'produit_nom', 'produit_description', 'produit_reference',
            'produit_image', 'prix_min', 'prix_max'
        ]
        read_only_fields = ['client', 'date_ajout']
    
    def get_produit_image(self, obj):
        try:
            image = obj.produit.imageproduit_set.filter(est_principale=True).first()
            if not image:
                image = obj.produit.imageproduit_set.first()
            return image.url_image if image else None
        except:
            return None
    
    def get_prix_min(self, obj):
        try:
            specs = obj.produit.specificationproduit_set.all()
            if specs:
                prix_list = [spec.prix_promo or spec.prix for spec in specs]
                return min(prix_list)
            return None
        except:
            return None
    
    def get_prix_max(self, obj):
        try:
            specs = obj.produit.specificationproduit_set.all()
            if specs:
                prix_list = [spec.prix_promo or spec.prix for spec in specs]
                return max(prix_list)
            return None
        except:
            return None

# ===== 5. SERIALIZERS COMMANDES =====

class DetailCommandeSerializer(serializers.ModelSerializer):
    specification_nom = serializers.CharField(source='specification.nom', read_only=True)
    produit_nom = serializers.CharField(source='specification.produit.nom', read_only=True)
    produit_image = serializers.SerializerMethodField()
    
    class Meta:
        model = DetailCommande
        fields = [
            'id', 'specification', 'quantite', 'prix_unitaire',
            'specification_nom', 'produit_nom', 'produit_image'
        ]
    
    def get_produit_image(self, obj):
        try:
            image = obj.specification.produit.imageproduit_set.filter(est_principale=True).first()
            if not image:
                image = obj.specification.produit.imageproduit_set.first()
            return image.url_image if image else None
        except:
            return None

class TrackingCommandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingCommande
        fields = ['ancien_statut', 'nouveau_statut', 'date_modification']

class CommandeSerializer(serializers.ModelSerializer):
    client_nom = serializers.SerializerMethodField()
    details = DetailCommandeSerializer(source='detailcommande_set', many=True)
    tracking_history = TrackingCommandeSerializer(many=True, read_only=True)
    nombre_articles = serializers.SerializerMethodField()

    class Meta:
        model = Commande
        fields = [
            'id', 'client', 'date_commande', 'montant_total', 'statut',
            'client_nom', 'details', 'tracking_history', 'nombre_articles'
        ]

    def get_client_nom(self, obj):
        try:
            return obj.client.nom if obj.client else "-"
        except:
            return "-"
    
    def get_nombre_articles(self, obj):
        try:
            return sum(detail.quantite for detail in obj.detailcommande_set.all())
        except:
            return 0

class ClientCommandeSerializer(serializers.ModelSerializer):
    """Serializer pour afficher les commandes côté client"""
    details = DetailCommandeSerializer(source='detailcommande_set', many=True, read_only=True)
    nombre_articles = serializers.SerializerMethodField()
    statut_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Commande
        fields = [
            'id', 'date_commande', 'montant_total', 'statut',
            'details', 'nombre_articles', 'statut_display'
        ]
        read_only_fields = ['client', 'date_commande']
    
    def get_nombre_articles(self, obj):
        try:
            return sum(detail.quantite for detail in obj.detailcommande_set.all())
        except:
            return 0
    
    def get_statut_display(self, obj):
        statuts = {
            'en_attente': 'En attente',
            'confirmee': 'Confirmée',
            'en_preparation': 'En préparation',
            'expedie': 'Expédiée',
            'livree': 'Livrée',
            'annulee': 'Annulée'
        }
        return statuts.get(obj.statut, obj.statut)

class CommandeCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une commande"""
    adresse_livraison = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Commande
        fields = ['adresse_livraison']

# ===== 6. AUTRES SERIALIZERS =====

class ClientCategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'description']

class DetailsClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetailsClient
        fields = ['nom', 'prenom', 'adresse', 'ville', 'code_postal', 'pays']

class DetailsCommercantSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetailsCommercant
        fields = [
            'nom_boutique', 'description_boutique', 'adresse_commerciale',
            'ville', 'code_postal', 'pays', 'commission_rate'
        ]

class ProfilVendeurSerializer(serializers.ModelSerializer):
    utilisateur = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = ProfilVendeur
        fields = [
            'id', 'utilisateur', 'nom_boutique', 'description', 'adresse', 
            'ville', 'telephone_professionnel', 'logo', 'est_approuve', 
            'total_ventes', 'evaluation', 'date_creation', 'date_modification'
        ]
        read_only_fields = [
            'utilisateur', 'est_approuve', 'total_ventes', 'evaluation', 
            'date_creation', 'date_modification'
        ]

class MouvementStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = MouvementStock
        fields = [
            'id', 'specification', 'quantite', 'type_mouvement', 
            'reference_document', 'commentaire', 'date_mouvement'
        ]
        read_only_fields = ['date_mouvement']

class NotificationSerializer(serializers.ModelSerializer):
    produit = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'produit', 'date_notification', 'message', 'est_lue']
        read_only_fields = ['date_notification', 'produit', 'message']

class AvisSerializer(serializers.ModelSerializer):
    client_nom = serializers.SerializerMethodField()
    produit_nom = serializers.CharField(source='produit.nom', read_only=True)
    
    class Meta:
        model = Avis
        fields = [
            'id', 'produit', 'client', 'note', 'commentaire', 
            'date_creation', 'client_nom', 'produit_nom'
        ]
        read_only_fields = ['client', 'date_creation']
    
    def get_client_nom(self, obj):
        try:
            if obj.client and obj.client.nom and obj.client.prenom:
                return f"{obj.client.prenom} {obj.client.nom[0]}."
            else:
                return "Client anonyme"
        except:
            return "Client anonyme"

class AvisCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un avis"""
    
    class Meta:
        model = Avis
        fields = ['produit', 'note', 'commentaire']
    
    def validate_note(self, value):
        """Valider la note"""
        if not (1 <= value <= 5):
            raise serializers.ValidationError("La note doit être entre 1 et 5")
        return value
    
    def validate_commentaire(self, value):
        """Valider le commentaire"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Le commentaire doit contenir au moins 10 caractères")
        return value.strip()

# ===== 7. SERIALIZER CLIENT POUR LES PRODUITS =====

class ClientProduitSerializer(serializers.ModelSerializer):
    """Version simplifiée pour les clients"""
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    prix_min = serializers.SerializerMethodField()
    prix_max = serializers.SerializerMethodField()
    image_principale = serializers.SerializerMethodField()
    note_moyenne = serializers.SerializerMethodField()
    nombre_avis = serializers.SerializerMethodField()
    
    class Meta:
        model = Produit
        fields = [
            'id', 'reference', 'nom', 'description', 'categorie', 'categorie_nom',
            'prix_min', 'prix_max', 'image_principale', 'note_moyenne', 'nombre_avis'
        ]
    
    def get_prix_min(self, obj):
        try:
            specs = obj.specificationproduit_set.all()
            if specs:
                prix_list = [spec.prix_promo if spec.prix_promo else spec.prix for spec in specs]
                return float(min(prix_list)) if prix_list else 0
            return 0
        except:
            return 0
    
    def get_prix_max(self, obj):
        try:
            specs = obj.specificationproduit_set.all()
            if specs:
                prix_list = [spec.prix_promo if spec.prix_promo else spec.prix for spec in specs]
                return float(max(prix_list)) if prix_list else 0
            return 0
        except:
            return 0
    
    def get_image_principale(self, obj):
        try:
            image = obj.imageproduit_set.filter(est_principale=True).first()
            if not image:
                image = obj.imageproduit_set.first()
            return image.url_image if image else None
        except:
            return None
    
    def get_note_moyenne(self, obj):
        try:
            return 4.2  # Simulé pour l'instant
        except:
            return 0
    
    def get_nombre_avis(self, obj):
        try:
            return 15  # Simulé pour l'instant
        except:
            return 0
        
# admin
class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer pour afficher les utilisateurs côté admin"""
    boutique_info = serializers.SerializerMethodField()
    commandes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Utilisateur
        fields = [
            'id_utilisateur', 'telephone', 'email', 'nom', 'prenom',
            'type_utilisateur', 'date_creation', 'date_modification',
            'est_verifie', 'est_actif', 'boutique_info', 'commandes_count'
        ]
    
    def get_boutique_info(self, obj):
        """Informations de la boutique si c'est un vendeur"""
        if obj.type_utilisateur == 'vendeur':
            try:
                profil = obj.profil_vendeur
                return {
                    'nom_boutique': profil.nom_boutique,
                    'ville': profil.ville,
                    'est_approuve': profil.est_approuve,
                    'evaluation': float(profil.evaluation),
                    'total_ventes': float(profil.total_ventes),
                }
            except:
                return None
        return None
    
    def get_commandes_count(self, obj):
        """Nombre de commandes pour ce client"""
        if obj.type_utilisateur == 'client':
            try:
                client = DetailsClient.objects.get(utilisateur=obj)
                return Commande.objects.filter(client=client).count()
            except:
                return 0
        return 0
    
class AdminBoutiqueSerializer(serializers.ModelSerializer):
    # """Serializer pour afficher les boutiques côté admin"""
    vendeur_nom = serializers.CharField(source='utilisateur.nom', read_only=True)
    vendeur_prenom = serializers.CharField(source='utilisateur.prenom', read_only=True)
    vendeur_telephone = serializers.CharField(source='utilisateur.telephone', read_only=True)
    vendeur_email = serializers.CharField(source='utilisateur.email', read_only=True)
    vendeur_actif = serializers.BooleanField(source='utilisateur.est_actif', read_only=True)
    produits_count = serializers.SerializerMethodField()
    commandes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProfilVendeur
        fields = [
            'id', 'nom_boutique', 'description', 'ville', 'adresse',
            'telephone_professionnel', 'est_approuve', 'total_ventes', 'evaluation',
            'date_creation', 'date_modification',
            'vendeur_nom', 'vendeur_prenom', 'vendeur_telephone', 'vendeur_email', 'vendeur_actif',
            'produits_count', 'commandes_count'
        ]
    
    def get_produits_count(self, obj):
        """Nombre de produits de cette boutique"""
        try:
            # Adapter selon votre modèle - ici j'assume que les produits ont un champ commercant
            return Produit.objects.filter(commercant=obj).count()
        except:
            return 0
    
    def get_commandes_count(self, obj):
        """Nombre de commandes pour cette boutique"""
        try:
            # Adapter selon votre modèle
            return 0  # À implémenter selon votre logique
        except:
            return 0

# Ajouts aux serializers.py existants

from rest_framework import serializers
from .models import (
    Produit, SignalementProduit, HistoriqueModerationProduit, 
    CritereQualiteProduit, EvaluationQualiteProduit
)

# ===== SERIALIZERS DE MODÉRATION =====

class SignalementProduitSerializer(serializers.ModelSerializer):
    """Serializer pour afficher les signalements"""
    produit_nom = serializers.CharField(source='produit.nom', read_only=True)
    produit_reference = serializers.CharField(source='produit.reference', read_only=True)
    signaleur_nom = serializers.SerializerMethodField()
    moderateur_nom = serializers.SerializerMethodField()
    type_signalement_display = serializers.CharField(source='get_type_signalement_display', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    
    class Meta:
        model = SignalementProduit
        fields = [
            'id', 'produit', 'produit_nom', 'produit_reference',
            'signaleur', 'signaleur_nom', 'type_signalement', 'type_signalement_display',
            'description', 'statut', 'statut_display', 'date_signalement',
            'date_traitement', 'moderateur', 'moderateur_nom', 'action_prise'
        ]
        read_only_fields = ['date_signalement']
    
    def get_signaleur_nom(self, obj):
        try:
            return f"{obj.signaleur.prenom or ''} {obj.signaleur.nom or ''}".strip() or "Utilisateur"
        except:
            return "Utilisateur"
    
    def get_moderateur_nom(self, obj):
        try:
            if obj.moderateur:
                return f"{obj.moderateur.prenom or ''} {obj.moderateur.nom or ''}".strip() or "Modérateur"
            return None
        except:
            return None


class SignalementProduitCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un signalement"""
    
    class Meta:
        model = SignalementProduit
        fields = ['produit', 'type_signalement', 'description']
    
    def validate_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("La description doit contenir au moins 10 caractères")
        return value.strip()


class HistoriqueModerationSerializer(serializers.ModelSerializer):
    """Serializer pour l'historique de modération"""
    moderateur_nom = serializers.SerializerMethodField()
    produit_nom = serializers.CharField(source='produit.nom', read_only=True)
    
    class Meta:
        model = HistoriqueModerationProduit
        fields = [
            'id', 'produit', 'produit_nom', 'moderateur', 'moderateur_nom',
            'action', 'ancien_statut', 'nouveau_statut', 'commentaire', 'date_action'
        ]
        read_only_fields = ['date_action']
    
    def get_moderateur_nom(self, obj):
        try:
            return f"{obj.moderateur.prenom or ''} {obj.moderateur.nom or ''}".strip() or "Modérateur"
        except:
            return "Modérateur"


class ProduitModerationSerializer(serializers.ModelSerializer):
    """Serializer spécialement pour la modération des produits"""
    
    # Champs calculés pour les détails
    nombre_signalements = serializers.SerializerMethodField()
    score_qualite_moyen = serializers.SerializerMethodField()
    derniers_signalements = SignalementProduitSerializer(
        source='signalements', many=True, read_only=True
    )
    historique_moderation = HistoriqueModerationSerializer(
        many=True, read_only=True
    )
    
    # Informations sur le vendeur
    vendeur_nom = serializers.SerializerMethodField()
    vendeur_est_verifie = serializers.SerializerMethodField()
    
    # Statistiques produit  
    total_ventes = serializers.SerializerMethodField()
    nombre_avis = serializers.SerializerMethodField()
    note_moyenne = serializers.SerializerMethodField()
    
    class Meta:
        model = Produit
        fields = [
            'id', 'nom', 'description', 'reference', 'categorie',
            'est_approuve', 'statut_moderation', 'date_moderation',
            'moderateur', 'raison_rejet', 'est_visible', 'score_qualite',
            'derniere_verification',
            'nombre_signalements', 'score_qualite_moyen',
            'derniers_signalements', 'historique_moderation',
            'vendeur_nom', 'vendeur_est_verifie',
            'total_ventes', 'nombre_avis', 'note_moyenne'
        ]
    
    def get_nombre_signalements(self, obj):
        try:
            return obj.signalements.filter(statut='nouveau').count()
        except:
            return 0
    
    def get_score_qualite_moyen(self, obj):
        try:
            evaluations = obj.evaluations_qualite.all()
            if evaluations:
                return sum(float(eval.score) for eval in evaluations) / len(evaluations)
            return 0
        except:
            return 0
    
    def get_vendeur_nom(self, obj):
        try:
            if obj.commercant:
                return obj.commercant.nom_boutique
            return "Vendeur inconnu"
        except:
            return "Vendeur inconnu"
    
    def get_vendeur_est_verifie(self, obj):
        try:
            return obj.commercant.est_verifie if obj.commercant else False
        except:
            return False
    
    def get_total_ventes(self, obj):
        try:
            # Compter les détails de commande pour ce produit
            from .models import DetailCommande
            return DetailCommande.objects.filter(
                specification__produit=obj
            ).aggregate(
                total=models.Sum('quantite')
            )['total'] or 0
        except:
            return 0
    
    def get_nombre_avis(self, obj):
        try:
            return obj.avis_set.count()
        except:
            return 0
    
    def get_note_moyenne(self, obj):
        try:
            avis = obj.avis_set.all()
            if avis:
                return sum(avis_item.note for avis_item in avis) / len(avis)
            return 0
        except:
            return 0


class ModerationActionSerializer(serializers.Serializer):
    """Serializer pour les actions de modération"""
    
    ACTION_CHOICES = [
        ('approuver', 'Approuver'),
        ('rejeter', 'Rejeter'),
        ('suspendre', 'Suspendre'),
        ('masquer', 'Masquer'),
        ('demander_modification', 'Demander modification'),
    ]
    
    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    commentaire = serializers.CharField(required=False, allow_blank=True)
    raison_rejet = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        if data['action'] == 'rejeter' and not data.get('raison_rejet'):
            raise serializers.ValidationError("La raison du rejet est requise")
        return data


class EvaluationQualiteSerializer(serializers.ModelSerializer):
    """Serializer pour l'évaluation qualité"""
    critere_nom = serializers.CharField(source='critere.nom', read_only=True)
    evaluateur_nom = serializers.SerializerMethodField()
    
    class Meta:
        model = EvaluationQualiteProduit
        fields = [
            'id', 'produit', 'critere', 'critere_nom', 'score',
            'commentaire', 'evaluateur', 'evaluateur_nom', 'date_evaluation'
        ]
        read_only_fields = ['evaluateur', 'date_evaluation']
    
    def get_evaluateur_nom(self, obj):
        try:
            return f"{obj.evaluateur.prenom or ''} {obj.evaluateur.nom or ''}".strip() or "Évaluateur"
        except:
            return "Évaluateur"


class CritereQualiteSerializer(serializers.ModelSerializer):
    """Serializer pour les critères de qualité"""
    
    class Meta:
        model = CritereQualiteProduit
        fields = ['id', 'nom', 'description', 'poids', 'est_actif']


# ===== MODIFICATION DU PRODUIT SERIALIZER EXISTANT =====


# admin notification 
class NotificationAdminSerializer(serializers.ModelSerializer):
    """Serializer étendu pour l'admin"""
    open_rate = serializers.SerializerMethodField()
    click_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = '__all__'
    
    def get_open_rate(self, obj):
        if obj.sent_count > 0:
            return (obj.opened_count / obj.sent_count) * 100
        return 0
    
    def get_click_rate(self, obj):
        if obj.sent_count > 0:
            return (obj.clicked_count / obj.sent_count) * 100
        return 0





class CampaignSerializer(serializers.ModelSerializer):
    """Serializer pour les campagnes marketing"""
    open_rate = serializers.ReadOnlyField()
    click_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = Campaign
        fields = [
            'id', 'title', 'content', 'type', 'target_users', 'channel', 
            'status', 'scheduled_date', 'sent_count', 'opened_count', 
            'clicked_count', 'created_at', 'updated_at', 'open_rate', 'click_rate'
        ]
        read_only_fields = ['status', 'sent_count', 'opened_count', 'clicked_count', 
                          'created_at', 'updated_at']


class CampaignCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer/modifier une campagne"""
    
    class Meta:
        model = Campaign
        fields = ['title', 'content', 'type', 'target_users', 'channel', 'scheduled_date']
    
    def validate_scheduled_date(self, value):
        """Handle both string and datetime input for scheduled_date"""
        if isinstance(value, str):
            try:
                # Try parsing with timezone first, then without
                try:
                    value = parser.isoparse(value)
                except ValueError:
                    value = parser.parse(value)
            except ValueError as e:
                raise serializers.ValidationError(
                    f"Format de date invalide. Utilisez YYYY-MM-DDTHH:MM:SS ou YYYY-MM-DD HH:MM:SS. Erreur: {str(e)}"
                )
        
        if value and value <= timezone.now():
            raise serializers.ValidationError("La date programmée doit être dans le futur")
        return value
class SystemAlertSerializer(serializers.ModelSerializer):
    """Serializer pour les alertes système"""
    
    class Meta:
        model = SystemAlert
        fields = [
            'id', 'title', 'description', 'type', 'severity', 'status',
            'affected_users', 'created_at', 'resolved_at'
        ]

class SystemAlertCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer/modifier une alerte"""
    
    class Meta:
        model = SystemAlert
        fields = [
            'title', 'description', 'type', 'severity', 'affected_users'
        ]

class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une notification"""
    
    class Meta:
        model = Notification
        fields = ['message', 'produit']
    
    def validate_message(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Le message doit contenir au moins 5 caractères")
        return value.strip()