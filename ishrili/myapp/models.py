from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class CategorieManager(models.Manager):
    def get_by_natural_key(self, nom):
        return self.get(nom=nom)

class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    objects = CategorieManager()
    
    def __str__(self):
        return self.nom
    
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

class Produit(models.Model):
    reference = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, related_name="produits")
    
    def __str__(self):
        return f"{self.nom} ({self.reference})"
    
    def get_specification_par_defaut(self):
        return self.specifications.filter(est_defaut=True).first()
    
    def get_prix(self):
        spec_defaut = self.get_specification_par_defaut()
        if spec_defaut:
            return spec_defaut.prix
        return None
    
    def get_image_principale(self):
        return self.images.filter(est_principale=True).first()
    
    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"

class ImageProduit(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name="images")
    url_image = models.ImageField(upload_to='produits/')
    est_principale = models.BooleanField(default=False)
    ordre = models.IntegerField(default=0)
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image de {self.produit.nom} ({self.est_principale and 'principale' or 'secondaire'})"
    
    def save(self, *args, **kwargs):
        # Si cette image est définie comme principale, désactivez toutes les autres images principales de ce produit
        if self.est_principale:
            ImageProduit.objects.filter(produit=self.produit, est_principale=True).update(est_principale=False)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Image du produit"
        verbose_name_plural = "Images des produits"
        ordering = ['ordre', '-est_principale']

class SpecificationProduit(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name="specifications")
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    prix_promo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    quantite_stock = models.IntegerField(default=0)
    est_defaut = models.BooleanField(default=False)
    reference_specification = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return f"{self.produit.nom} - {self.nom}"
    
    def save(self, *args, **kwargs):
        # Si cette spécification est définie comme défaut, désactivez toutes les autres spécifications par défaut de ce produit
        if self.est_defaut:
            SpecificationProduit.objects.filter(produit=self.produit, est_defaut=True).update(est_defaut=False)
        super().save(*args, **kwargs)
    
    def get_prix_actuel(self):
        return self.prix_promo if self.prix_promo else self.prix
    
    class Meta:
        verbose_name = "Spécification du produit"
        verbose_name_plural = "Spécifications des produits"

class UtilisateurManager(BaseUserManager):
    def create_user(self, email, nom, prenom, password=None, **extra_fields):
        if not email:
            raise ValueError('L\'adresse email est obligatoire')
        email = self.normalize_email(email)
        user = self.model(email=email, nom=nom, prenom=prenom, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, nom, prenom, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        
        return self.create_user(email, nom, prenom, password, **extra_fields)

class Utilisateur(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('client', 'Client'),
        ('vendeur', 'Vendeur'),
        ('admin', 'Administrateur'),
    ]
    
    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    ville = models.CharField(max_length=100, blank=True, null=True)
    code_postal = models.CharField(max_length=10, blank=True, null=True)
    pays = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_inscription = models.DateTimeField(auto_now_add=True)
    
    objects = UtilisateurManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom']
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

class Commande(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('validee', 'Validée'),
        ('en_preparation', 'En préparation'),
        ('expediee', 'Expédiée'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    ]
    
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name="commandes")
    date_commande = models.DateTimeField(default=timezone.now)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=30, choices=STATUT_CHOICES, default='en_attente')
    
    def __str__(self):
        return f"Commande #{self.id} - {self.utilisateur}"
    
    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-date_commande']

class DetailCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name="details")
    specification = models.ForeignKey(SpecificationProduit, on_delete=models.SET_NULL, null=True)
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Détail commande #{self.commande.id} - {self.specification}"
    
    def get_total(self):
        return self.prix_unitaire * self.quantite
    
    class Meta:
        verbose_name = "Détail de commande"
        verbose_name_plural = "Détails de commande"

class Avis(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name="avis")
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True)
    note = models.IntegerField()
    commentaire = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Avis de {self.utilisateur} sur {self.produit}"
    
    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        ordering = ['-date_creation']
        constraints = [
            models.CheckConstraint(check=models.Q(note__gte=1, note__lte=5), name='note_entre_1_et_5')
        ]

class Panier(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="panier")
    specification = models.ForeignKey(SpecificationProduit, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Panier de {self.utilisateur}: {self.specification} x{self.quantite}"
    
    def get_total(self):
        return self.specification.get_prix_actuel() * self.quantite
    
    class Meta:
        verbose_name = "Article du panier"
        verbose_name_plural = "Articles du panier"

class Favori(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="favoris")
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name="favoris")
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Favori de {self.utilisateur}: {self.produit}"
    
    class Meta:
        verbose_name = "Favori"
        verbose_name_plural = "Favoris"
        unique_together = ('utilisateur', 'produit')

class MouvementStock(models.Model):
    TYPE_CHOICES = [
        ('entree', 'Entrée'),
        ('sortie', 'Sortie'),
        ('ajustement', 'Ajustement'),
        ('commande', 'Commande'),
        ('retour', 'Retour'),
    ]
    
    specification = models.ForeignKey(SpecificationProduit, on_delete=models.CASCADE, related_name="mouvements_stock")
    quantite = models.IntegerField(help_text="Positif pour entrée, négatif pour sortie")
    type_mouvement = models.CharField(max_length=30, choices=TYPE_CHOICES)
    reference_document = models.CharField(max_length=50, blank=True, null=True, help_text="Référence de commande, bon de livraison, etc.")
    date_mouvement = models.DateTimeField(default=timezone.now)
    commentaire = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.get_type_mouvement_display()} de {abs(self.quantite)} pour {self.specification}"
    
    def save(self, *args, **kwargs):
        # Mise à jour automatique du stock de la spécification
        self.specification.quantite_stock += self.quantite
        self.specification.save()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"
        ordering = ['-date_mouvement']