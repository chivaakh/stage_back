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


class Produit(models.Model):
    reference = models.CharField(max_length=50)
    nom = models.CharField(max_length=200)
    description = models.TextField()
    categorie = models.ForeignKey('Categorie', on_delete=models.SET_NULL, null=True)
    commercant = models.ForeignKey('DetailsCommercant', on_delete=models.CASCADE, null=True, blank=True)


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
    quantite = models.IntegerField()
    date_ajout = models.DateTimeField(auto_now_add=True)


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
    produit = models.ForeignKey('Produit', on_delete=models.CASCADE)
    date_notification = models.DateTimeField(default=timezone.now)
    message = models.TextField()
    est_lue = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification {self.produit.nom} - {self.date_notification.strftime('%Y-%m-%d')}"

# Ajouter ce modèle à votre models.py existant

