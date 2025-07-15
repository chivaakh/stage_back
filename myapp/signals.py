# signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from .models import Utilisateur

@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    """Crée l'utilisateur administrateur par défaut après les migrations"""
    if sender.name == 'myapp':  # Remplacez 'myapp' par le nom de votre application Django
        
        # Données de l'administrateur selon vos spécifications
        admin_data = {
            'email': 'yahyanna13@gmail.com',
            'telephone': '38393738',
            'nom': 'Mohamed',
            'prenom': 'yahya',
            'mot_de_passe': 'admin',
            'type_utilisateur': 'administrateur'  # Utilise votre modèle, pas le système Django
        }
        
        # Vérifier si l'admin existe déjà (par email ou téléphone)
        admin_exists_email = Utilisateur.objects.filter(email=admin_data['email']).exists()
        admin_exists_phone = Utilisateur.objects.filter(telephone=admin_data['telephone']).exists()
        
        if not admin_exists_email and not admin_exists_phone:
            try:
                # Créer l'utilisateur administrateur avec votre modèle Utilisateur
                admin = Utilisateur(
                    email=admin_data['email'],
                    telephone=admin_data['telephone'],
                    nom=admin_data['nom'],
                    prenom=admin_data['prenom'],
                    mot_de_passe=make_password(admin_data['mot_de_passe']),
                    type_utilisateur=admin_data['type_utilisateur'],
                    est_verifie=True,
                    est_actif=True,
                    methode_verification='email',
                    date_creation=timezone.now(),
                    date_modification=timezone.now()
                )
                admin.save()
                
                print('🛡️  ====== ADMINISTRATEUR CRÉÉ ======')
                print(f'   📧 Email: {admin_data["email"]}')
                print(f'   📱 Téléphone: {admin_data["telephone"]}')
                print(f'   👤 Nom: {admin_data["prenom"]} {admin_data["nom"]}')
                print(f'   🔑 Mot de passe: {admin_data["mot_de_passe"]}')
                print(f'   🎯 Type: {admin_data["type_utilisateur"]}')
                print('   ✅ Redirection: /admin')
                print('   ⚠️  IMPORTANT: Changez le mot de passe après la première connexion!')
                print('======================================')
                
            except Exception as e:
                print(f'❌ Erreur lors de la création de l\'administrateur: {str(e)}')
                
        elif admin_exists_email:
            print(f'ℹ️  Administrateur avec email {admin_data["email"]} existe déjà')
        elif admin_exists_phone:
            print(f'ℹ️  Administrateur avec téléphone {admin_data["telephone"]} existe déjà')