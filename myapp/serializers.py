# from rest_framework import serializers/
# from .models import Produit, ImageProduit, SpecificationProduit, 

# myapp/serializers_client.py - Serializers spécifiques aux clients

from rest_framework import serializers
from .models import Produit, ImageProduit, SpecificationProduit, Utilisateur, ProfilVendeur, TrackingCommande, Utilisateur
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Utilisateur, DetailsClient, DetailsCommercant
from .models import (
    Produit, ImageProduit, SpecificationProduit, 
    Utilisateur, 
    # PasswordResetToken,
    DetailsClient, DetailCommande, DetailsCommercant,
    Categorie,  # ← CELUI-CI ÉTAIT MANQUANT !
    Notification, Commande, DetailCommande, 
    TrackingCommande, Avis, Panier, Favori, 
    MouvementStock
)


class SignupSerializer(serializers.ModelSerializer):
    prenom = serializers.CharField(write_only=True, required=True)
    nom = serializers.CharField(required=False, allow_blank=True)
    mot_de_passe = serializers.CharField(write_only=True, required=True, min_length=6)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)  #  AJOUT DE allow_null=True
    telephone = serializers.CharField(required=True)

    class Meta:
        model = Utilisateur
        fields = ['nom', 'prenom', 'email', 'telephone', 'mot_de_passe']

    def validate(self, data):
        if not data.get('email') and not data.get('telephone'):
            raise serializers.ValidationError("Email ou téléphone doit être renseigné.")
        
        # Gérer l'email : convertir vide ou None en None
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
        
        # S'assurer que email vide devient None
        if validated_data.get('email') == '':
            validated_data['email'] = None
            
        utilisateur = Utilisateur(**validated_data)
        utilisateur.mot_de_passe = make_password(mot_de_passe)
        utilisateur.type_utilisateur = type_utilisateur
        utilisateur.save()
        return utilisateur




class LoginSerializer(serializers.Serializer):
    identifiant = serializers.CharField(required=True)  # email ou téléphone
    mot_de_passe = serializers.CharField(required=True, write_only=True)
from .models import ImageProduit, SpecificationProduit, Produit

# ===== SERIALIZER IMAGES PRODUIT =====
class ImageProduitSerializer(serializers.ModelSerializer):
    """Serializer pour les images de produits"""
    produit_nom = serializers.CharField(source='produit.nom', read_only=True)
    # url_complete = serializers.SerializerMethodField()
    # taille_fichier = serializers.SerializerMethodField()
    
    class Meta:
        model = ImageProduit
        fields = [
            'id', 'produit', 'url_image', 'est_principale', 'ordre', 
            'date_ajout', 'produit_nom']
        # read_only_fields = ['date_ajout']
    
    

    
    # def get_prix_final(self, obj):
    #     """Prix final (promo si disponible, sinon prix normal)"""
    #     return obj.prix_promo if obj.prix_promo else obj.prix
    
    # def get_pourcentage_promo(self, obj):
    #     """Pourcentage de réduction si promo"""
    #     if obj.prix_promo and obj.prix_promo < obj.prix:
    #         reduction = ((obj.prix - obj.prix_promo) / obj.prix) * 100
    #         return round(reduction, 1)
    #     return 0
    
    # def get_statut_stock(self, obj):
    #     """Statut du stock"""
    #     if obj.quantite_stock <= 0:
    #         return "rupture"
    #     elif obj.quantite_stock <= 5:
    #         return "faible"
    #     elif obj.quantite_stock <= 20:
    #         return "moyen"
    #     else:
    #         return "bon"
    
    # def get_valeur_stock(self, obj):
    #     """Valeur totale du stock"""
    #     prix_unitaire = obj.prix_promo if obj.prix_promo else obj.prix
    #     return float(prix_unitaire * obj.quantite_stock)
    
    # def validate_nom(self, value):
    #     """Valider le nom de la spécification"""
    #     if not value or len(value.strip()) < 2:
    #         raise serializers.ValidationError("Le nom doit contenir au moins 2 caractères")
    #     return value.strip()
    
    # def validate_prix(self, value):
    #     """Valider le prix"""
    #     if value <= 0:
    #         raise serializers.ValidationError("Le prix doit être positif")
    #     if value > 999999.99:
    #         raise serializers.ValidationError("Prix trop élevé")
    #     return value
    
    # def validate_prix_promo(self, value):
    #     """Valider le prix promo"""
    #     if value is not None:
    #         if value <= 0:
    #             raise serializers.ValidationError("Le prix promo doit être positif")
    #         if value > 999999.99:
    #             raise serializers.ValidationError("Prix promo trop élevé")
    #     return value
    
    # def validate_quantite_stock(self, value):
    #     """Valider la quantité en stock"""
    #     if value < 0:
    #         raise serializers.ValidationError("La quantité en stock ne peut pas être négative")
    #     if value > 999999:
    #         raise serializers.ValidationError("Quantité en stock trop élevée")
    #     return value
    
    # def validate(self, data):
    #     """Validation globale"""
    #     prix = data.get('prix')
    #     prix_promo = data.get('prix_promo')
    #     produit = data.get('produit')
    #     est_defaut = data.get('est_defaut', False)
        
    #     # Vérifier que le prix promo est inférieur au prix normal
    #     if prix_promo and prix and prix_promo >= prix:
    #         raise serializers.ValidationError({
    #             'prix_promo': 'Le prix promo doit être inférieur au prix normal'
    #         })
        
    #     # Si c'est marqué comme spécification par défaut, vérifier qu'il n'y en a pas déjà une
    #     if est_defaut and produit:
    #         queryset = SpecificationProduit.objects.filter(produit=produit, est_defaut=True)
    #         if self.instance:
    #             queryset = queryset.exclude(id=self.instance.id)
            
    #         if queryset.exists():
    #             # Ne pas lever d'erreur, mais signaler qu'on va remplacer
    #             pass  # La vue gérera le remplacement
        
    #     return data

class SpecificationProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecificationProduit
        fields = [
            'id', 'produit', 'nom', 'description', 'prix', 'prix_promo', 
            'quantite_stock', 'est_defaut', 'reference_specification'
        ]
# REMPLACEZ votre ClientProduitSerializer par cette version ULTRA SIMPLE :

class ClientProduitSerializer(serializers.ModelSerializer):
    """Version ultra simple sans erreurs"""
    
    class Meta:
        model = Produit
        fields = ['id', 'reference', 'nom', 'description', 'categorie']
    
    def to_representation(self, instance):
        """Ajouter des données calculées de façon sûre"""
        data = super().to_representation(instance)
        
        # Ajouter prix min de façon sécurisée
        try:
            spec = instance.specificationproduit_set.first()
            if spec:
                data['prix_min'] = float(spec.prix)
                data['prix_max'] = float(spec.prix)
            else:
                data['prix_min'] = 0
                data['prix_max'] = 0
        except:
            data['prix_min'] = 0
            data['prix_max'] = 0
        
        # Ajouter image principale de façon sécurisée
        try:
            image = instance.imageproduit_set.first()
            data['image_principale'] = image.url_image if image else None
        except:
            data['image_principale'] = None
        
        # Ajouter nom de catégorie
        try:
            data['categorie_nom'] = instance.categorie.nom if instance.categorie else None
        except:
            data['categorie_nom'] = None
        
        return data

    # def get_prix_min(self, obj):
    #     specs = obj.specificationproduit_set.all()
    #     if specs:
    #         prix_list = [spec.prix_promo if spec.prix_promo else spec.prix for spec in specs]
    #         return min(prix_list) if prix_list else None
    #     return None

    # def get_prix_max(self, obj):
    #     specs = obj.specificationproduit_set.all()
    #     if specs:
    #         prix_list = [spec.prix_promo if spec.prix_promo else spec.prix for spec in specs]
    #         return max(prix_list) if prix_list else None
    #     return None

    # def get_image_principale(self, obj):
    #     image = obj.imageproduit_set.filter(est_principale=True).first()
    #     if not image:
    #         image = obj.imageproduit_set.first()
    #     return image.url_image if image else None

    # def get_note_moyenne(self, obj):
    #     # Simuler une note pour l'instant
    #     return 4.2

    # def get_nombre_avis(self, obj):
    #     # Simuler le nombre d'avis
    #     return 15

class ClientCategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'description']


# À ajouter dans votre serializers.py

from rest_framework import serializers
from .models import (
    Produit, Panier, Favori, Avis, Commande, DetailCommande, 
    SpecificationProduit, DetailsClient, ImageProduit
)

# ===== SERIALIZERS PANIER =====
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
        """Récupère l'image principale du produit"""
        try:
            image = obj.specification.produit.imageproduit_set.filter(est_principale=True).first()
            if not image:
                image = obj.specification.produit.imageproduit_set.first()
            return image.url_image if image else None
        except:
            return None
    
    def get_prix_unitaire(self, obj):
        """Prix unitaire (promo si disponible, sinon prix normal)"""
        return float(obj.specification.prix_promo or obj.specification.prix)
    
    def get_prix_total(self, obj):
        """Prix total pour cette ligne"""
        prix_unitaire = obj.specification.prix_promo or obj.specification.prix
        return float(prix_unitaire * obj.quantite)

class PanierCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer/modifier des articles du panier"""
    
    class Meta:
        model = Panier
        fields = ['specification', 'quantite']
    
    def validate_quantite(self, value):
        """Valider la quantité"""
        if value <= 0:
            raise serializers.ValidationError("La quantité doit être supérieure à 0")
        if value > 100:  # ✅ AJOUT: Limite raisonnable
            raise serializers.ValidationError("Quantité maximum : 100")
        return value
    
    def validate_specification(self, value):
        """Valider que la spécification existe et a du stock"""
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
            # ✅ AJOUT: Vérifier stock disponible + quantité déjà dans panier
            if self.instance:  # Update existant
                if quantite > specification.quantite_stock:
                    raise serializers.ValidationError(
                        f"Quantité demandée ({quantite}) supérieure au stock disponible ({specification.quantite_stock})"
                    )
            else:  # Nouvel ajout
                panier_existant = Panier.objects.filter(
                    client=self.context['request'].user.detailsclient,
                    specification=specification
                ).first()
                
                quantite_totale = quantite
                if panier_existant:
                    quantite_totale += panier_existant.quantite
                
                if quantite_totale > specification.quantite_stock:
                    raise serializers.ValidationError(
                        f"Quantité totale ({quantite_totale}) supérieure au stock disponible ({specification.quantite_stock})"
                    )
        
        return data

# ===== SERIALIZERS FAVORIS =====
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
        """Image principale du produit"""
        try:
            image = obj.produit.imageproduit_set.filter(est_principale=True).first()
            if not image:
                image = obj.produit.imageproduit_set.first()
            return image.url_image if image else None
        except:
            return None
    
    def get_prix_min(self, obj):
        """Prix minimum des spécifications"""
        try:
            specs = obj.produit.specificationproduit_set.all()
            if specs:
                prix_list = [spec.prix_promo or spec.prix for spec in specs]
                return min(prix_list)
            return None
        except:
            return None
    
    def get_prix_max(self, obj):
        """Prix maximum des spécifications"""
        try:
            specs = obj.produit.specificationproduit_set.all()
            if specs:
                prix_list = [spec.prix_promo or spec.prix for spec in specs]
                return max(prix_list)
            return None
        except:
            return None

# ===== SERIALIZERS AVIS =====
class AvisSerializer(serializers.ModelSerializer):
    """Serializer pour afficher les avis"""
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
        """Nom du client (anonymisé)"""
        try:
            if obj.client.nom and obj.client.prenom:
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

# ===== SERIALIZERS COMMANDES =====
class DetailCommandeSerializer(serializers.ModelSerializer):
    """Serializer pour les détails de commande"""
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
        """Image du produit"""
        try:
            image = obj.specification.produit.imageproduit_set.filter(est_principale=True).first()
            if not image:
                image = obj.specification.produit.imageproduit_set.first()
            return image.url_image if image else None
        except:
            return None

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
        """Nombre total d'articles dans la commande"""
        return sum(detail.quantite for detail in obj.detailcommande_set.all())
    
    def get_statut_display(self, obj):
        """Affichage lisible du statut"""
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
    
    def validate(self, data):
        """Validation lors de la création"""
        # Ici vous pouvez ajouter des validations spécifiques
        return data
    
    def create(self, validated_data):
        """Logique de création de commande"""
        # Cette méthode sera appelée lors de la création
        # La logique métier sera dans la vue
        return validated_data

# ===== SERIALIZER POUR LE PROFIL CLIENT =====


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


class SignupWithDetailsSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    telephone = serializers.CharField(required=True)
    mot_de_passe = serializers.CharField(write_only=True, min_length=6)
    role = serializers.ChoiceField(choices=[('client','Client'),('vendeur','Vendeur')])
    details_client = DetailsClientSerializer(required=False)
    details_commercant = DetailsCommercantSerializer(required=False)

    def validate(self, data):
        # un seul des deux doit être présent selon le rôle
        if data['role'] == 'client' and 'details_client' not in data:
            raise serializers.ValidationError("Les détails client sont obligatoires.")
        if data['role'] == 'vendeur' and 'details_commercant' not in data:
            raise serializers.ValidationError("Les détails commerçant sont obligatoires.")
        return data

    def create(self, validated_data):
        from django.contrib.auth.hashers import make_password
        from .models import Utilisateur, DetailsClient, DetailsCommercant

        details_client_data = validated_data.pop('details_client', None)
        details_commercant_data = validated_data.pop('details_commercant', None)
        pwd = validated_data.pop('mot_de_passe')
        utilisateur = Utilisateur.objects.create(
            email=validated_data['email'],
            telephone=validated_data['telephone'],
            mot_de_passe=make_password(pwd),
            type_utilisateur=validated_data['role']
        )
        # créer le profil associé
        if utilisateur.type_utilisateur == 'client':
            DetailsClient.objects.create(utilisateur=utilisateur, **details_client_data)
        else:
            # on fixe est_verifie à False, note_moyenne à 0.00 par défaut
            DetailsCommercant.objects.create(
                utilisateur=utilisateur,
                **details_commercant_data
            )
        return utilisateur



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


from .models import Produit
from .models import SpecificationProduit, MouvementStock



class ProduitSerializer(serializers.ModelSerializer):
    # CORRECTION : Utiliser le bon nom de relation
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




# class SpecificationProduitSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SpecificationProduit
#         fields = ['id', 'produit', 'nom', 'quantite_stock', 'prix', 'prix_promo']
#         read_only_fields = ['produit', 'nom', 'prix', 'prix_promo']  # On ne modifie que la quantité ici

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

# class DetailCommandeSerializer(serializers.ModelSerializer):
#     id = serializers.IntegerField(required=False)  # permet l’update via id
#     specification = serializers.PrimaryKeyRelatedField(queryset=SpecificationProduit.objects.all())
#     specification_nom = serializers.CharField(source='specification.nom', read_only=True)
#     class Meta:
#         model = DetailCommande
#         fields = ['id', 'quantite', 'prix_unitaire', 'specification', 'specification_nom']


class TrackingCommandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingCommande  # Référence correcte au modèle
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
    
    
