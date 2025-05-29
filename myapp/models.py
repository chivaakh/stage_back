from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UtilisateurManager(BaseUserManager):
    def create_user(self, email, telephone, password=None, **extra_fields):
        if not email:
            raise ValueError('L\'adresse email est obligatoire')
        email = self.normalize_email(email)
        user = self.model(email=email, telephone=telephone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, telephone, password=None, **extra_fields):
        extra_fields.setdefault('est_actif', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        
        return self.create_user(email, telephone, password, **extra_fields)


class Utilisateur(AbstractBaseUser, PermissionsMixin):
    ROLES = (
        ('client', 'Client'),
        ('commercant', 'Commerçant'),
        ('admin', 'Administrateur'),
    )
    
    email = models.EmailField(max_length=100, unique=True)
    telephone = models.CharField(max_length=20)
    date_inscription = models.DateTimeField(auto_now_add=True)
    derniere_connexion = models.DateTimeField(auto_now=True)
    est_actif = models.BooleanField(default=True)
    role = models.CharField(max_length=20, choices=ROLES)
    
    # Champs requis par Django
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # Ces champs sont obligatoires quand on utilise AbstractBaseUser
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['telephone']
    
    # Aussi obligatoire avec AbstractBaseUser
    objects = UtilisateurManager()
    
    # Résoudre les conflits avec les accesseurs inverses
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='utilisateur_set',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='utilisateur_set',
    )


class ImageUtilisateur(models.Model):
    utilisateur = models.ForeignKey('Utilisateur', on_delete=models.CASCADE)
    url_image = models.CharField(max_length=255)
    type_image = models.CharField(max_length=50)
    date_ajout = models.DateTimeField(auto_now_add=True)


class DetailsClient(models.Model):
    utilisateur = models.OneToOneField('Utilisateur', on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    adresse = models.TextField()
    ville = models.CharField(max_length=100)
    code_postal = models.CharField(max_length=10)
    pays = models.CharField(max_length=50)
    photo_profil = models.ForeignKey('ImageUtilisateur', on_delete=models.SET_NULL, null=True, blank=True)


class DetailsCommercant(models.Model):
    utilisateur = models.OneToOneField('Utilisateur', on_delete=models.CASCADE)
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


class DetailCommande(models.Model):
    commande = models.ForeignKey('Commande', on_delete=models.CASCADE)
    specification = models.ForeignKey('SpecificationProduit', on_delete=models.CASCADE)
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)


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
    admin = models.ForeignKey('Utilisateur', on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    details = models.TextField()
    date_heure = models.DateTimeField(auto_now_add=True)