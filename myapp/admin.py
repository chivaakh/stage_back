from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Utilisateur, ImageUtilisateur, DetailsClient, DetailsCommercant,
    Categorie, Produit, ImageProduit, SpecificationProduit,
    Commande, DetailCommande, Avis, Panier, Favori, MouvementStock, JournalAdmin
)

# Configuration pour le modèle Utilisateur personnalisé
class UtilisateurAdmin(UserAdmin):
    list_display = ('email', 'telephone', 'role', 'est_actif', 'date_inscription')
    list_filter = ('role', 'est_actif', 'date_inscription')
    search_fields = ('email', 'telephone')
    ordering = ('-date_inscription',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('telephone', 'role')}),
        ('Permissions', {'fields': ('est_actif', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_inscription')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'telephone', 'password1', 'password2', 'role', 'est_actif'),
        }),
    )


# Configuration pour le modèle DetailsClient avec une relation inline pour les photos
class ImageUtilisateurInline(admin.TabularInline):
    model = ImageUtilisateur
    extra = 1
    fk_name = 'utilisateur'


# Configurations pour les détails clients et commerçants
class DetailsClientAdmin(admin.ModelAdmin):
    list_display = ('get_email', 'nom', 'prenom', 'ville', 'pays')
    search_fields = ('nom', 'prenom', 'utilisateur__email')
    
    def get_email(self, obj):
        return obj.utilisateur.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'utilisateur__email'


class DetailsCommercantAdmin(admin.ModelAdmin):
    list_display = ('get_email', 'nom_boutique', 'ville', 'est_verifie', 'note_moyenne')
    list_filter = ('est_verifie', 'ville')
    search_fields = ('nom_boutique', 'utilisateur__email')
    
    def get_email(self, obj):
        return obj.utilisateur.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'utilisateur__email'


# Configuration pour les produits avec images et spécifications inline
class ImageProduitInline(admin.TabularInline):
    model = ImageProduit
    extra = 1


class SpecificationProduitInline(admin.TabularInline):
    model = SpecificationProduit
    extra = 1


class ProduitAdmin(admin.ModelAdmin):
    list_display = ('reference', 'nom', 'categorie', 'get_commercant')
    list_filter = ('categorie', 'commercant__nom_boutique')
    search_fields = ('nom', 'reference', 'description')
    inlines = [ImageProduitInline, SpecificationProduitInline]
    
    def get_commercant(self, obj):
        return obj.commercant.nom_boutique
    get_commercant.short_description = 'Commerçant'
    get_commercant.admin_order_field = 'commercant__nom_boutique'


# Configuration pour les commandes avec détails inline
class DetailCommandeInline(admin.TabularInline):
    model = DetailCommande
    extra = 1


class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_client', 'date_commande', 'montant_total', 'statut')
    list_filter = ('statut', 'date_commande')
    search_fields = ('client__nom', 'client__prenom', 'id')
    inlines = [DetailCommandeInline]
    
    def get_client(self, obj):
        return f"{obj.client.nom} {obj.client.prenom}"
    get_client.short_description = 'Client'
    get_client.admin_order_field = 'client__nom'


# Configuration pour les autres modèles
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description')
    search_fields = ('nom',)


class AvisAdmin(admin.ModelAdmin):
    list_display = ('produit', 'client', 'note', 'date_creation')
    list_filter = ('note', 'date_creation')
    search_fields = ('commentaire', 'produit__nom', 'client__nom')


class PanierAdmin(admin.ModelAdmin):
    list_display = ('client', 'specification', 'quantite', 'date_ajout')
    list_filter = ('date_ajout',)
    search_fields = ('client__nom', 'specification__produit__nom')


class FavoriAdmin(admin.ModelAdmin):
    list_display = ('client', 'produit', 'date_ajout')
    list_filter = ('date_ajout',)
    search_fields = ('client__nom', 'produit__nom')


class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ('specification', 'quantite', 'type_mouvement', 'date_mouvement')
    list_filter = ('type_mouvement', 'date_mouvement')
    search_fields = ('specification__produit__nom', 'reference_document', 'commentaire')


class JournalAdminAdmin(admin.ModelAdmin):
    list_display = ('admin', 'action', 'date_heure')
    list_filter = ('action', 'date_heure')
    search_fields = ('admin__email', 'action', 'details')
    readonly_fields = ('admin', 'action', 'details', 'date_heure')


# Enregistrement des modèles avec leurs configurations
admin.site.register(Utilisateur, UtilisateurAdmin)
admin.site.register(DetailsClient, DetailsClientAdmin)
admin.site.register(DetailsCommercant, DetailsCommercantAdmin)
admin.site.register(Categorie, CategorieAdmin)
admin.site.register(Produit, ProduitAdmin)
admin.site.register(Commande, CommandeAdmin)
admin.site.register(Avis, AvisAdmin)
admin.site.register(Panier, PanierAdmin)
admin.site.register(Favori, FavoriAdmin)
admin.site.register(MouvementStock, MouvementStockAdmin)
admin.site.register(JournalAdmin, JournalAdminAdmin)

# Pour les modèles qui n'ont pas besoin de configuration spéciale,
# vous pouvez les enregistrer simplement:
admin.site.register(ImageUtilisateur)
admin.site.register(ImageProduit)
admin.site.register(SpecificationProduit)
admin.site.register(DetailCommande)