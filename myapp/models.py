from django.db import models
import uuid
from datetime import timedelta
from django.utils import timezone



class Utilisateur(models.Model):
    TYPE_UTILISATEUR_CHOICES = [
        ('client', 'Client'),
        ('vendeur', 'Vendeur'),
        ('administrateur', 'Administrateur'),
    ]

    METHODE_VERIFICATION_CHOICES = [
        ('sms', 'SMS'),
        ('email', 'Email'),
    ]

    id_utilisateur = models.AutoField(primary_key=True)
    telephone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    mot_de_passe = models.CharField(max_length=128)  # correspond au hash du mot de passe
    nom = models.CharField(max_length=100, null=True, blank=True)
    prenom = models.CharField(max_length=100, null=True, blank=True)
    type_utilisateur = models.CharField(max_length=15, choices=TYPE_UTILISATEUR_CHOICES)
    date_creation = models.DateTimeField(default=timezone.now)
    date_modification = models.DateTimeField(auto_now=True)
    est_verifie = models.BooleanField(default=False)
    methode_verification = models.CharField(max_length=10, choices=METHODE_VERIFICATION_CHOICES, null=True, blank=True)
    est_actif = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Convertir email vide en None pour respecter l'unicité
        if self.email == '':
            self.email = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom or ''} ({self.telephone})"

    
class PasswordResetToken(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.date_expiration:
            self.date_expiration = timezone.now() + timedelta(hours=1)  # token valable 1h
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.date_expiration



class ProfilVendeur(models.Model):
    utilisateur = models.OneToOneField(
        Utilisateur, 
        on_delete=models.CASCADE, 
        related_name='profil_vendeur',
        limit_choices_to={'type_utilisateur': 'vendeur'}
    )
    nom_boutique = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    ville = models.CharField(max_length=100)
    telephone_professionnel = models.CharField(max_length=20, blank=True, null=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    taux_commission = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    est_approuve = models.BooleanField(default=False)
    total_ventes = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    evaluation = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Boutique : {self.nom_boutique} (Vendeur ID: {self.utilisateur.id_utilisateur})"














class ImageUtilisateur(models.Model):
    utilisateur = models.ForeignKey('Utilisateur', on_delete=models.CASCADE, to_field='id_utilisateur')
    url_image = models.CharField(max_length=255)
    type_image = models.CharField(max_length=50)
    date_ajout = models.DateTimeField(auto_now_add=True)


class DetailsClient(models.Model):
    utilisateur = models.OneToOneField('Utilisateur', on_delete=models.CASCADE, to_field='id_utilisateur')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    adresse = models.TextField()
    ville = models.CharField(max_length=100)
    code_postal = models.CharField(max_length=10)
    pays = models.CharField(max_length=50)
    photo_profil = models.ForeignKey('ImageUtilisateur', on_delete=models.SET_NULL, null=True, blank=True)


class DetailsCommercant(models.Model):
    utilisateur = models.OneToOneField('Utilisateur', on_delete=models.CASCADE, to_field='id_utilisateur')
    nom_boutique = models.CharField(max_length=200)
    description_boutique = models.TextField()
    adresse_commerciale = models.TextField()
    ville = models.CharField(max_length=100)
    code_postal = models.CharField(max_length=10)
    pays = models.CharField(max_length=50)
    est_verifie = models.BooleanField(default=False)
    note_moyenne = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    logo = models.ForeignKey('ImageUtilisateur', on_delete=models.SET_NULL, null=True, blank=True)


class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()



# MODIFIER le modèle Produit
class Produit(models.Model):
    reference = models.CharField(max_length=50)
    nom = models.CharField(max_length=200)
    description = models.TextField()
    categorie = models.ForeignKey('Categorie', on_delete=models.SET_NULL, null=True)
    
    #NOUVEAU : Lier directement au ProfilVendeur au lieu de DetailsCommercant
    vendeur = models.ForeignKey('ProfilVendeur', on_delete=models.CASCADE, null=True, blank=True, related_name='produits')
    
    #GARDER commercant pour compatibilité (optionnel)
    commercant = models.ForeignKey('DetailsCommercant', on_delete=models.CASCADE, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        #NOUVEAU : Auto-associer commercant si vendeur est défini
        if self.vendeur and not self.commercant:
            try:
                # Chercher le DetailsCommercant associé au vendeur
                self.commercant = DetailsCommercant.objects.get(
                    utilisateur=self.vendeur.utilisateur
                )
            except DetailsCommercant.DoesNotExist:
                # Créer DetailsCommercant si n'existe pas
                self.commercant = DetailsCommercant.objects.create(
                    utilisateur=self.vendeur.utilisateur,
                    nom_boutique=self.vendeur.nom_boutique,
                    description_boutique=self.vendeur.description or "",
                    ville=self.vendeur.ville,
                    est_verifie=self.vendeur.est_approuve
                )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} - {self.vendeur.nom_boutique if self.vendeur else 'Sans vendeur'}"
    # wethi9a hye ldaret 4e l3ad lahi y5assar shi gl3uh 
    # jout de champs au modèle Produit existant (migration nécessaire)
    # NOUVEAUX CHAMPS POUR LA MODÉRATION
    STATUT_MODERATION_CHOICES = [
        ('en_attente', 'En attente de modération'),
        ('approuve', 'Approuvé'),
        ('rejete', 'Rejeté'),
        ('suspendu', 'Suspendu'),
    ]
    
    est_approuve = models.BooleanField(default=False)
    statut_moderation = models.CharField(
        max_length=20, 
        choices=STATUT_MODERATION_CHOICES, 
        default='en_attente'
    )
    date_moderation = models.DateTimeField(null=True, blank=True)
    moderateur = models.ForeignKey(
        'Utilisateur', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='produits_moderes'
    )
    raison_rejet = models.TextField(blank=True, null=True)
    est_visible = models.BooleanField(default=True)  # Pour masquer sans supprimer
    
    # Métadonnées de qualité
    score_qualite = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    derniere_verification = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Auto-approbation si le vendeur est vérifié (optionnel)
        if (self.commercant and 
            hasattr(self.commercant, 'est_verifie') and 
            self.commercant.est_verifie and 
            self.statut_moderation == 'en_attente'):
            self.est_approuve = True
            self.statut_moderation = 'approuve'
            self.date_moderation = timezone.now()
        
        super().save(*args, **kwargs)


class SignalementProduit(models.Model):
    """Modèle pour gérer les signalements de produits"""
    
    TYPE_SIGNALEMENT_CHOICES = [
        ('contenu_inapproprie', 'Contenu inapproprié'),
        ('fausse_information', 'Fausse information'),
        ('prix_anormal', 'Prix anormal'),
        ('image_trompeuse', 'Image trompeuse'),
        ('spam', 'Spam'),
        ('violation_droits', 'Violation de droits'),
        ('autre', 'Autre'),
    ]
    
    STATUT_SIGNALEMENT_CHOICES = [
        ('nouveau', 'Nouveau'),
        ('en_cours', 'En cours de traitement'),
        ('traite', 'Traité'),
        ('rejete', 'Rejeté'),
    ]
    
    produit = models.ForeignKey(
        Produit, 
        on_delete=models.CASCADE, 
        related_name='signalements'
    )
    signaleur = models.ForeignKey(
        'Utilisateur', 
        on_delete=models.CASCADE,
        related_name='signalements_envoyes'
    )
    type_signalement = models.CharField(
        max_length=30, 
        choices=TYPE_SIGNALEMENT_CHOICES
    )
    description = models.TextField()
    statut = models.CharField(
        max_length=20, 
        choices=STATUT_SIGNALEMENT_CHOICES, 
        default='nouveau'
    )
    date_signalement = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    moderateur = models.ForeignKey(
        'Utilisateur', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='signalements_traites'
    )
    action_prise = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['produit', 'signaleur']  # Un signalement par utilisateur par produit
        ordering = ['-date_signalement']
    
    def __str__(self):
        return f"Signalement {self.get_type_signalement_display()} - {self.produit.nom}"


class HistoriqueModerationProduit(models.Model):
    """Historique des actions de modération sur les produits"""
    
    produit = models.ForeignKey(
        Produit, 
        on_delete=models.CASCADE, 
        related_name='historique_moderation'
    )
    moderateur = models.ForeignKey(
        'Utilisateur', 
        on_delete=models.CASCADE
    )
    action = models.CharField(max_length=50)  # 'approuve', 'rejete', 'suspendu', etc.
    ancien_statut = models.CharField(max_length=20, blank=True)
    nouveau_statut = models.CharField(max_length=20)
    commentaire = models.TextField(blank=True)
    date_action = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_action']
    
    def __str__(self):
        return f"{self.action} - {self.produit.nom} - {self.date_action.strftime('%Y-%m-%d')}"


class CritereQualiteProduit(models.Model):
    """Critères d'évaluation de la qualité des produits"""
    
    nom = models.CharField(max_length=100)
    description = models.TextField()
    poids = models.DecimalField(max_digits=3, decimal_places=2, default=1.00)  # Importance du critère
    est_actif = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nom


class EvaluationQualiteProduit(models.Model):
    """Évaluation de la qualité d'un produit selon les critères"""
    
    produit = models.ForeignKey(
        Produit, 
        on_delete=models.CASCADE, 
        related_name='evaluations_qualite'
    )
    critere = models.ForeignKey(CritereQualiteProduit, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=3, decimal_places=2)  # Score de 0 à 10
    commentaire = models.TextField(blank=True)
    evaluateur = models.ForeignKey('Utilisateur', on_delete=models.CASCADE)
    date_evaluation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['produit', 'critere']
    
    def __str__(self):
        return f"{self.produit.nom} - {self.critere.nom}: {self.score}/10"

class ImageProduit(models.Model):
    produit = models.ForeignKey('Produit', on_delete=models.CASCADE)
    url_image = models.CharField(max_length=255)
    est_principale = models.BooleanField(default=False)
    ordre = models.IntegerField(default=0)
    date_ajout = models.DateTimeField(auto_now_add=True)


class SpecificationProduit(models.Model):
    produit = models.ForeignKey('Produit', on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    prix_promo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantite_stock = models.IntegerField(default=0)
    est_defaut = models.BooleanField(default=False)
    reference_specification = models.CharField(max_length=50)


class Commande(models.Model):
    client = models.ForeignKey('DetailsClient', on_delete=models.CASCADE)
    date_commande = models.DateTimeField(auto_now_add=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=30, default='en_attente')
    # admin 
    est_litigieuse = models.BooleanField(default=False)
    raison_litige = models.TextField(blank=True, null=True)
    date_resolution_litige = models.DateTimeField(blank=True, null=True)
    
    # Choix de statuts étendus
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirmee', 'Confirmée'),
        ('en_preparation', 'En préparation'),
        ('expedie', 'Expédiée'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
        ('litigieuse', 'Litigieuse'),  # NOUVEAU
        ('remboursee', 'Remboursée'),  # NOUVEAU
    ]
    


    def save(self, *args, **kwargs):
        # Récupérer l'ancien statut si c'est une mise à jour
        if self.pk:
            old_instance = Commande.objects.get(pk=self.pk)
            old_status = old_instance.statut
        else:
            old_status = None
            
        super().save(*args, **kwargs)
        
        # Créer l'entrée de tracking si le statut a changé
        if old_status != self.statut:
            TrackingCommande.objects.create(
                commande=self,
                ancien_statut=old_status,
                nouveau_statut=self.statut
            )


class DetailCommande(models.Model):
    commande = models.ForeignKey('Commande', on_delete=models.CASCADE)
    specification = models.ForeignKey('SpecificationProduit', on_delete=models.CASCADE)
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

class TrackingCommande(models.Model):
    commande = models.ForeignKey('Commande', on_delete=models.CASCADE, related_name='tracking_history')
    ancien_statut = models.CharField(max_length=30, blank=True, null=True)
    nouveau_statut = models.CharField(max_length=30)
    date_modification = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_modification']
        verbose_name = "Historique de commande"
        verbose_name_plural = "Historiques de commandes"



class Avis(models.Model):
    produit = models.ForeignKey('Produit', on_delete=models.CASCADE)
    client = models.ForeignKey('DetailsClient', on_delete=models.CASCADE)
    note = models.IntegerField()
    commentaire = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)


class Panier(models.Model):
    client = models.ForeignKey('DetailsClient', on_delete=models.CASCADE)
    specification = models.ForeignKey('SpecificationProduit', on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)  # ✅ CHANGE: PositiveIntegerField
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)  # ✅ AJOUT: Track modifications
    
    class Meta:
        unique_together = ['client', 'specification']  # ✅ AJOUT: Éviter doublons
        ordering = ['-date_modification']
    
    def __str__(self):
        return f"{self.client.nom} - {self.specification.nom} x{self.quantite}"


class Favori(models.Model):
    client = models.ForeignKey('DetailsClient', on_delete=models.CASCADE)
    produit = models.ForeignKey('Produit', on_delete=models.CASCADE)
    date_ajout = models.DateTimeField(auto_now_add=True)


class MouvementStock(models.Model):
    specification = models.ForeignKey('SpecificationProduit', on_delete=models.CASCADE)
    quantite = models.IntegerField()
    type_mouvement = models.CharField(max_length=30)
    reference_document = models.CharField(max_length=50, blank=True, null=True)
    date_mouvement = models.DateTimeField(auto_now_add=True)
    commentaire = models.TextField(blank=True, null=True)


class JournalAdmin(models.Model):
    admin = models.ForeignKey('Utilisateur', on_delete=models.CASCADE, to_field='id_utilisateur')
    action = models.CharField(max_length=255)
    details = models.TextField()
    date_heure = models.DateTimeField(auto_now_add=True)
    
 

class Notification(models.Model):
    produit = models.ForeignKey('Produit', on_delete=models.CASCADE, null=True, blank=True)
    date_notification = models.DateTimeField(default=timezone.now)
    message = models.TextField()
    est_lue = models.BooleanField(default=False)
     # ... vos champs existants ...
    
    # NOUVEAUX CHAMPS pour l'admin :
    title = models.CharField(max_length=200, blank=True, null=True)  # Titre
    target_users = models.CharField(max_length=50, default='all')    # all, clients, vendeurs
    channel = models.CharField(max_length=20, default='push')        # push, email, sms
    priority = models.CharField(max_length=20, default='medium')     # low, medium, high, urgent
    scheduled_date = models.DateTimeField(blank=True, null=True)     # Programmation
    sent_count = models.IntegerField(default=0)                     # Nb envoyées
    opened_count = models.IntegerField(default=0)                   # Nb ouvertes
    clicked_count = models.IntegerField(default=0)                  # Nb cliquées
    
    # Choix pour les champs
    TARGET_CHOICES = [
        ('all', 'Tous les utilisateurs'),
        ('clients', 'Clients uniquement'),
        ('vendeurs', 'Vendeurs uniquement'),
        ('active', 'Utilisateurs actifs'),
    ]
    
    CHANNEL_CHOICES = [
        ('push', 'Notification Push'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('in-app', 'In-App'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Basse'),
        ('medium', 'Moyenne'),
        ('high', 'Haute'),
        ('urgent', 'Urgente'),
    ]


    def __str__(self):
        return f"Notification {self.produit.nom} - {self.date_notification.strftime('%Y-%m-%d')}"

# Ajouter ce modèle à votre models.py existant

class Campaign(models.Model):
    """Modèle pour les campagnes marketing"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    type = models.CharField(max_length=50, choices=[
        ('promotional', 'Promotion'),
        ('newsletter', 'Newsletter'),
        ('announcement', 'Annonce'),
    ])
    target_users = models.CharField(max_length=50, default='all')
    channel = models.CharField(max_length=20, default='email')
    status = models.CharField(max_length=20, default='draft', choices=[
        ('draft', 'Brouillon'),
        ('scheduled', 'Programmée'),
        ('active', 'Active'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
    ])
    scheduled_date = models.DateTimeField(blank=True, null=True)
    sent_count = models.IntegerField(default=0)
    opened_count = models.IntegerField(default=0)
    clicked_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def open_rate(self):
        if self.sent_count > 0:
            return (self.opened_count / self.sent_count) * 100
        return 0

    @property
    def click_rate(self):
        if self.sent_count > 0:
            return (self.clicked_count / self.sent_count) * 100
        return 0

class SystemAlert(models.Model):
    """Modèle pour les alertes système"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    type = models.CharField(max_length=50, choices=[
        ('technical', 'Technique'),
        ('system', 'Système'),
        ('security', 'Sécurité'),
        ('performance', 'Performance'),
    ])
    severity = models.CharField(max_length=20, choices=[
        ('info', 'Information'),
        ('warning', 'Attention'),
        ('critical', 'Critique'),
    ])
    status = models.CharField(max_length=20, default='active', choices=[
        ('active', 'Active'),
        ('resolved', 'Résolue'),
        ('investigating', 'En cours'),
    ])
    affected_users = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
