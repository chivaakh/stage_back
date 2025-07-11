# serializers.py - VERSION CORRIGÉE AVEC BON ORDRE

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import (
    Produit, ImageProduit, SpecificationProduit, 
    Utilisateur, ProfilVendeur, DetailsClient, DetailsCommercant,
    Categorie, Notification, Commande, DetailCommande, 
    TrackingCommande, Avis, Panier, Favori, MouvementStock
)

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

class ProduitSerializer(serializers.ModelSerializer):
    """Serializer principal pour les produits"""
    images = ImageProduitSerializer(many=True, read_only=True, source='imageproduit_set')
    specifications = SpecificationProduitSerializer(many=True, read_only=True, source='specificationproduit_set')
    
    # ✅ MAINTENANT CategorieSerializer EST DÉFINI
    categorie = CategorieSerializer(read_only=True)
    categorie_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    # ✅ CHAMPS CALCULÉS SÉCURISÉS
    prix_min = serializers.SerializerMethodField()
    prix_max = serializers.SerializerMethodField()
    stock_total = serializers.SerializerMethodField()
    image_principale = serializers.SerializerMethodField()
    
    class Meta:
        model = Produit
        fields = [
            'id', 'nom', 'description', 'reference', 'commercant',
            'categorie', 'categorie_id', 
            'images', 'specifications',
            'prix_min', 'prix_max', 'stock_total', 'image_principale'
        ]
        extra_kwargs = {
            'commercant': {'required': False, 'allow_null': True},
        }
    
    def get_prix_min(self, obj):
        """Prix minimum parmi toutes les spécifications"""
        try:
            specs = obj.specificationproduit_set.all()
            if specs:
                prix_list = [spec.prix_promo if spec.prix_promo else spec.prix for spec in specs]
                return float(min(prix_list)) if prix_list else 0
            return 0
        except:
            return 0
    
    def get_prix_max(self, obj):
        """Prix maximum parmi toutes les spécifications"""
        try:
            specs = obj.specificationproduit_set.all()
            if specs:
                prix_list = [spec.prix_promo if spec.prix_promo else spec.prix for spec in specs]
                return float(max(prix_list)) if prix_list else 0
            return 0
        except:
            return 0
    
    def get_stock_total(self, obj):
        """Stock total de toutes les spécifications"""
        try:
            specs = obj.specificationproduit_set.all()
            return sum(spec.quantite_stock for spec in specs)
        except:
            return 0
    
    def get_image_principale(self, obj):
        """Image principale du produit"""
        try:
            image_principale = obj.imageproduit_set.filter(est_principale=True).first()
            if image_principale:
                return {
                    'id': image_principale.id,
                    'url_image': image_principale.url_image,
                    'ordre': image_principale.ordre
                }
            # Si pas d'image principale, prendre la première
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
        """Créer un produit avec catégorie"""
        categorie_id = validated_data.pop('categorie_id', None)
        produit = Produit.objects.create(**validated_data)
        
        if categorie_id:
            try:
                categorie = Categorie.objects.get(id=categorie_id)
                produit.categorie = categorie
                produit.save()
            except Categorie.DoesNotExist:
                pass
        
        return produit
    
    def update(self, instance, validated_data):
        """Mettre à jour un produit avec catégorie"""
        categorie_id = validated_data.pop('categorie_id', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if categorie_id is not None:
            try:
                if categorie_id == '' or categorie_id is None:
                    instance.categorie = None
                else:
                    categorie = Categorie.objects.get(id=categorie_id)
                    instance.categorie = categorie
            except Categorie.DoesNotExist:
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