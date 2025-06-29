# myapp/views.py - VERSION FINALE COMPLÈTE ET CORRIGÉE ✅

# Imports groupés et organisés
# myapp/views.py - VERSION COMPLÈTE avec tous les ViewSets
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import Produit, ImageProduit, SpecificationProduit, Utilisateur, PasswordResetToken
from .serializers import ProduitSerializer, ImageProduitSerializer, SpecificationProduitSerializer , SignupSerializer, LoginSerializer
import logging
import os
import uuid
import logging
import traceback
from .models import DetailsClient,DetailCommande,DetailsCommercant

from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
from .models import Utilisateur
# Imports locaux
from .models import (
    Produit, ImageProduit, SpecificationProduit, MouvementStock,
    Categorie, Notification, Commande, DetailCommande
)
from .serializers import (
    ProduitSerializer, ImageProduitSerializer, SpecificationProduitSerializer,
    MouvementStockSerializer, CategorieSerializer, NotificationSerializer,
    CommandeSerializer, DetailCommandeSerializer
)
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import uuid
from rest_framework.views import APIView
logger = logging.getLogger(__name__)
from rest_framework import viewsets
# from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny 
from . import serializers
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.db import transaction
import requests
from django.utils.crypto import get_random_string
from .serializers import SignupWithDetailsSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

# À ajouter dans views.py - Vue SignupView simple
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            print("🔍 DEBUG: SignupView simple")
            
            # Données de base
            email = request.data.get('email')
            mot_de_passe = request.data.get('mot_de_passe')
            telephone = request.data.get('telephone')
            
            # Validations
            if not email or not mot_de_passe:
                return Response({
                    'error': 'Email et mot de passe requis'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Vérification existence
            if Utilisateur.objects.filter(email=email).exists():
                return Response({
                    'error': 'Un utilisateur avec cet email existe déjà'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Création utilisateur simple
            utilisateur = Utilisateur(
                email=email,
                telephone=telephone or '',
                type_utilisateur='client'  # Type par défaut
            )
            utilisateur.mot_de_passe = make_password(mot_de_passe)
            utilisateur.save()
            
            return Response({
                'message': 'Utilisateur créé avec succès',
                'user_id': utilisateur.id_utilisateur
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"❌ SignupView error: {e}")
            return Response({
                'error': f'Erreur: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SignupWithDetailsView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            print("🔍 DEBUG: Début signup-with-details")
            print(f"🔍 DEBUG: Données reçues: {request.data}")
            
            # 1. Extraction des données principales
            email = request.data.get('email')
            mot_de_passe = request.data.get('mot_de_passe')
            telephone = request.data.get('telephone')
            role = request.data.get('role')
            
            print(f"🔍 DEBUG: email={email}, role={role}, telephone={telephone}")
            
            # 2. Validations de base
            if not email or not mot_de_passe:
                return Response({
                    'error': 'Email et mot de passe requis'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not role or role not in ['client', 'vendeur', 'administrateur']:
                return Response({
                    'error': 'Rôle requis (client, vendeur ou administrateur)'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 3. Vérifier si l'utilisateur existe déjà
            if Utilisateur.objects.filter(email=email).exists():
                return Response({
                    'error': 'Un utilisateur avec cet email existe déjà'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 4. Création avec transaction
            with transaction.atomic():
                print("🔍 DEBUG: Création de l'utilisateur...")
                
                # ✅ SOLUTION DE CONTOURNEMENT : Créer d'abord l'utilisateur
                utilisateur = Utilisateur(
                    email=email,
                    telephone=telephone or '',
                    type_utilisateur=role
                )
                
                # Ajouter le mot de passe après création
                utilisateur.mot_de_passe = make_password(mot_de_passe)
                
                # Sauvegarder
                utilisateur.save()
                
                print(f"✅ DEBUG: Utilisateur créé avec ID: {utilisateur.id_utilisateur}")
                
                # 5. Traitement des détails selon le rôle
                if role == 'client':
                    details_client = request.data.get('details_client', {})
                    print(f"🔍 DEBUG: Détails client: {details_client}")
                    
                    # Créer le profil client séparé
                    if details_client:
                        DetailsClient.objects.create(
                            utilisateur=utilisateur,
                            nom=details_client.get('nom', ''),
                            prenom=details_client.get('prenom', ''),
                            adresse=details_client.get('adresse', ''),
                            ville=details_client.get('ville', ''),
                            code_postal=details_client.get('code_postal', ''),
                            pays=details_client.get('pays', ''),
                        )
                        print("✅ DEBUG: Profil client créé")
                    
                elif role == 'vendeur':  # Note: 'commercant' -> 'vendeur' selon votre modèle
                    details_commercant = request.data.get('details_commercant', {})
                    print(f"🔍 DEBUG: Détails commerçant: {details_commercant}")
                    
                    # Créer le profil commerçant séparé
                    if details_commercant:
                        DetailsCommercant.objects.create(
                            utilisateur=utilisateur,
                            nom_boutique=details_commercant.get('nom_boutique', ''),
                            description_boutique=details_commercant.get('description_boutique', ''),
                            adresse_commerciale=details_commercant.get('adresse_commerciale', ''),
                            ville=details_commercant.get('ville', ''),
                            code_postal=details_commercant.get('code_postal', ''),
                            pays=details_commercant.get('pays', ''),
                            est_verifie=False,
                            note_moyenne=0.00,
                            commission_rate=details_commercant.get('commission_rate', 5.0),
                        )
                        print("✅ DEBUG: Profil commerçant créé")
                
                print("✅ DEBUG: Inscription réussie")
                return Response({
                    'message': 'Inscription réussie',
                    'user_id': utilisateur.id_utilisateur,
                    'email': utilisateur.email,
                    'role': utilisateur.type_utilisateur
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            print(f"❌ DEBUG: Erreur générale: {e}")
            print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
            return Response({
                'error': f'Erreur interne: {str(e)}',
                'debug': traceback.format_exc() if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifiant = serializer.validated_data['identifiant']
        mot_de_passe = serializer.validated_data['mot_de_passe']

        try:
            utilisateur = Utilisateur.objects.get(
                Q(email=identifiant) | Q(telephone=identifiant)
            )
        except Utilisateur.DoesNotExist:
            return Response({"error": "Identifiant ou mot de passe incorrect."}, status=401)

        if not check_password(mot_de_passe, utilisateur.mot_de_passe):
            return Response({"error": "Identifiant ou mot de passe incorrect."}, status=401)

        # Ne pas utiliser login() ici, faire une session manuelle
        request.session['user_id'] = utilisateur.id_utilisateur  # stocker l'id dans la session

        return Response({"message": "Connexion réussie"}, status=200)



# Dans views.py - Vue SignupWithDetails corrigée
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.contrib.auth.hashers import make_password
import traceback
import json

class SignupWithDetailsView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            print("🔍 DEBUG: Début signup-with-details")
            print(f"🔍 DEBUG: Données reçues: {request.data}")
            
            # 1. Extraction des données principales
            email = request.data.get('email')
            mot_de_passe = request.data.get('mot_de_passe')
            telephone = request.data.get('telephone')
            role = request.data.get('role')
            
            print(f"🔍 DEBUG: email={email}, role={role}, telephone={telephone}")
            
            # 2. Validations de base
            if not email or not mot_de_passe:
                return Response({
                    'error': 'Email et mot de passe requis'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not role or role not in ['client', 'commercant']:
                return Response({
                    'error': 'Rôle requis (client ou commercant)'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 3. Vérifier si l'utilisateur existe déjà
            if Utilisateur.objects.filter(email=email).exists():
                return Response({
                    'error': 'Un utilisateur avec cet email existe déjà'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 4. Création avec transaction
            with transaction.atomic():
                print("🔍 DEBUG: Création de l'utilisateur...")
                
                # Créer l'utilisateur principal
                utilisateur = Utilisateur.objects.create(
                    email=email,
                    mot_de_passe=make_password(mot_de_passe),
                    telephone=telephone or '',
                    type_utilisateur=role
                )
                
                print(f"✅ DEBUG: Utilisateur créé avec ID: {utilisateur.id_utilisateur}")
                
                # 5. Traitement des détails selon le rôle
                if role == 'client':
                    details_client = request.data.get('details_client', {})
                    print(f"🔍 DEBUG: Détails client: {details_client}")
                    
                    # Mettre à jour les champs utilisateur avec les détails client
                    if details_client.get('nom'):
                        utilisateur.nom = details_client['nom']
                    if details_client.get('prenom'):
                        utilisateur.prenom = details_client['prenom']
                    
                    # Si vous avez un modèle DetailsClient séparé, créez-le ici
                    # DetailsClient.objects.create(
                    #     utilisateur=utilisateur,
                    #     adresse=details_client.get('adresse', ''),
                    #     ville=details_client.get('ville', ''),
                    #     code_postal=details_client.get('code_postal', ''),
                    #     pays=details_client.get('pays', ''),
                    # )
                    
                elif role == 'commercant':
                    details_commercant = request.data.get('details_commercant', {})
                    print(f"🔍 DEBUG: Détails commerçant: {details_commercant}")
                    
                    # Si vous avez un modèle DetailsCommercant, créez-le ici
                    # DetailsCommercant.objects.create(
                    #     utilisateur=utilisateur,
                    #     nom_boutique=details_commercant.get('nom_boutique', ''),
                    #     description_boutique=details_commercant.get('description_boutique', ''),
                    #     adresse_commerciale=details_commercant.get('adresse_commerciale', ''),
                    #     ville=details_commercant.get('ville', ''),
                    #     code_postal=details_commercant.get('code_postal', ''),
                    #     pays=details_commercant.get('pays', ''),
                    #     est_verifie=False,
                    #     note_moyenne=0.0,
                    #     commission_rate=details_commercant.get('commission_rate', 5.0),
                    # )
                
                # Sauvegarder les modifications
                utilisateur.save()
                
                print("✅ DEBUG: Inscription réussie")
                return Response({
                    'message': 'Inscription réussie',
                    'user_id': utilisateur.id_utilisateur,
                    'email': utilisateur.email,
                    'role': utilisateur.type_utilisateur
                }, status=status.HTTP_201_CREATED)
                
        except json.JSONDecodeError as e:
            print(f"❌ DEBUG: Erreur JSON: {e}")
            return Response({
                'error': 'Format JSON invalide'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            print(f"❌ DEBUG: Erreur générale: {e}")
            print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
            return Response({
                'error': f'Erreur interne: {str(e)}',
                'debug': traceback.format_exc() if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email requis"}, status=400)

        try:
            utilisateur = Utilisateur.objects.get(email=email)
        except Utilisateur.DoesNotExist:
            return Response({"error": "Email non trouvé"}, status=404)

        # Créer un token
        token_obj = PasswordResetToken.objects.create(utilisateur=utilisateur)

        # Construire URL de reset (à adapter à ton frontend)
        reset_url = f"https://localhost:5173/reset-password/{token_obj.token}"

        # Envoyer email
        send_mail(
            "Réinitialisation du mot de passe",
            f"Pour réinitialiser votre mot de passe, cliquez sur ce lien : {reset_url}",
            "no-reply@tonapp.com",
            [email],
        )

        return Response({"message": "Email envoyé si compte existant"}, status=200)



class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, token):
        mot_de_passe = request.data.get('mot_de_passe')
        if not mot_de_passe:
            return Response({"error": "Mot de passe requis"}, status=400)

        try:
            token_obj = PasswordResetToken.objects.get(token=token)
        except PasswordResetToken.DoesNotExist:
            return Response({"error": "Token invalide"}, status=404)

        if token_obj.is_expired():
            return Response({"error": "Token expiré"}, status=400)

        utilisateur = token_obj.utilisateur
        utilisateur.mot_de_passe = make_password(mot_de_passe)
        utilisateur.save()

        # Supprimer ou invalider le token
        token_obj.delete()

        return Response({"message": "Mot de passe réinitialisé avec succès"}, status=200)




class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "Token requis"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Valider le token Google et récupérer les infos utilisateur
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), "128897548037-fi6qsoqngat2rg46apt6pq6tfspbfcp3.apps.googleusercontent.com")

            # idinfo contient les infos utilisateur validées
            email = idinfo.get("email")
            nom = idinfo.get("family_name") or ""
            prenom = idinfo.get("given_name") or ""
            google_sub = idinfo.get("sub")  # id Google unique

            if not email:
                return Response({"error": "Email non trouvé dans le token"}, status=status.HTTP_400_BAD_REQUEST)

            # Recherche ou création utilisateur dans ta base
            with transaction.atomic():
                telephone_temporaire = f"google_{get_random_string(length=10)}"
                utilisateur, created = Utilisateur.objects.get_or_create(
                    email=email,
                    defaults={
                        "nom": nom,
                        "prenom": prenom,
                        "telephone": telephone_temporaire,  # tu peux gérer ça comme tu veux
                        "mot_de_passe": make_password(google_sub),  # hash d'une valeur unique Google
                        "type_utilisateur": "vendeur",  # ou ce que tu veux par défaut
                    },
                )

            # Ici tu peux créer une session manuelle ou un JWT selon ton auth backend
            request.session['user_id'] = utilisateur.id_utilisateur

            return Response({
                "message": "Connexion Google réussie",
                "user": {
                    "email": utilisateur.email,
                    "nom": utilisateur.nom,
                    "prenom": utilisateur.prenom,
                }
            }, status=status.HTTP_200_OK)

        # except ValueError:
        #     # Token invalide
        #     return Response({"error": "Token invalide"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            import traceback
            print("Erreur Google token :", e)
            traceback.print_exc()
            return Response({"error": f"Token invalide : {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)




class FacebookLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        access_token = request.data.get("access_token")
        email = request.data.get("email")

        if not access_token or not email:
            return Response({"error": "Token et email requis"}, status=status.HTTP_400_BAD_REQUEST)

        # Valider le token Facebook
        url = f'https://graph.facebook.com/me?access_token={access_token}&fields=email,name'
        response = requests.get(url)
        if response.status_code != 200:
            return Response({"error": "Token Facebook invalide"}, status=status.HTTP_400_BAD_REQUEST)

        facebook_data = response.json()
        name = facebook_data.get("name")
        if not name:
            return Response({"error": "Nom non trouvé dans le token"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            utilisateur, created = Utilisateur.objects.get_or_create(email=email)
            # Met à jour les infos à chaque login Facebook
            utilisateur.nom = name.split(" ")[-1]
            utilisateur.prenom = " ".join(name.split(" ")[:-1])
            if not utilisateur.telephone:
                utilisateur.telephone = ""  # ou une valeur par défaut si tu veux
            utilisateur.mot_de_passe = make_password(email)  # idéalement, un mot de passe généré ou token
            if not utilisateur.type_utilisateur:
                utilisateur.type_utilisateur = "vendeur"
            utilisateur.save()

        return Response({
            "message": "Connexion Facebook réussie",
            "created": created,
            "user": {
                "email": utilisateur.email,
                "nom": utilisateur.nom,
                "prenom": utilisateur.prenom,
                "telephone": utilisateur.telephone,
                "type_utilisateur": utilisateur.type_utilisateur,
            }
        }, status=status.HTTP_200_OK)



# Configuration du logger
logger = logging.getLogger(__name__)


# ===========================
# VIEWSETS PRINCIPAUX
# ===========================

class ProduitViewSet(viewsets.ModelViewSet):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Optimiser les requêtes avec prefetch"""
        return Produit.objects.prefetch_related(
            'imageproduit_set', 'specificationproduit_set'
        ).select_related('commercant', 'categorie')

    def create(self, request, *args, **kwargs):
        """Créer un produit avec images et spécifications - VERSION FINALE"""
        logger.info(f"🔍 Données reçues pour création: {request.data}")
        
        try:
            with transaction.atomic():
                # 1. Extraire les données avec CATEGORIE
                produit_data = {
                    'nom': request.data.get('nom'),
                    'description': request.data.get('description'),
                    'reference': request.data.get('reference'),
                }
                
                # ✅ AJOUTER la catégorie si fournie
                if request.data.get('categorie'):
                    produit_data['categorie'] = request.data.get('categorie')
                
                images_data = request.data.get('images', [])
                specifications_data = request.data.get('specifications', [])
                
                logger.info(f"📦 Produit: {produit_data}")
                logger.info(f"🖼️ Images reçues: {len(images_data)} images")
                logger.info(f"📋 Spécifications: {len(specifications_data)} specs")
                
                # DEBUG: Afficher le détail des images
                for i, img_data in enumerate(images_data):
                    logger.info(f"🖼️ Image {i+1}: {img_data}")
                
                # 2. Créer le produit de base
                produit_serializer = ProduitSerializer(data=produit_data)
                if produit_serializer.is_valid():
                    produit = produit_serializer.save()
                    logger.info(f"✅ Produit créé avec ID: {produit.id}")
                    
                    # 3. Ajouter les images
                    images_creees = 0
                    for i, image_data in enumerate(images_data):
                        if image_data.get('url_image'):  # Vérifier que l'URL existe
                            try:
                                image_obj = ImageProduit.objects.create(
                                    produit=produit,
                                    url_image=image_data['url_image'],
                                    est_principale=image_data.get('est_principale', False),
                                    ordre=image_data.get('ordre', i)
                                )
                                images_creees += 1
                                logger.info(f"✅ Image {i+1} créée: ID={image_obj.id}, URL={image_obj.url_image}")
                            except Exception as e:
                                logger.error(f"❌ Erreur création image {i+1}: {str(e)}")
                    
                    logger.info(f"📸 Total images créées: {images_creees}")
                    
                    # 4. Ajouter les spécifications
                    specs_creees = 0
                    for spec_data in specifications_data:
                        if spec_data.get('nom') and spec_data.get('prix'):  # Vérifier données minimales
                            try:
                                spec_obj = SpecificationProduit.objects.create(
                                    produit=produit,
                                    nom=spec_data['nom'],
                                    description=spec_data.get('description', ''),
                                    prix=float(spec_data['prix']),
                                    prix_promo=float(spec_data['prix_promo']) if spec_data.get('prix_promo') else None,
                                    quantite_stock=int(spec_data.get('quantite_stock', 0)),
                                    est_defaut=spec_data.get('est_defaut', False),
                                    reference_specification=spec_data.get('reference_specification', '')
                                )
                                specs_creees += 1
                                logger.info(f"✅ Spécification créée: {spec_obj.nom}")
                            except Exception as e:
                                logger.error(f"❌ Erreur création spécification: {str(e)}")
                    
                    logger.info(f"📋 Total spécifications créées: {specs_creees}")
                    
                    # 5. Retourner le produit complet avec relations
                    produit_complet = self.get_queryset().get(id=produit.id)
                    
                    # DEBUG: Vérifier que les images sont bien liées
                    images_liees = produit_complet.imageproduit_set.all()
                    logger.info(f"🔍 Vérification: {len(images_liees)} images liées au produit")
                    for img in images_liees:
                        logger.info(f"🔍 Image liée: ID={img.id}, URL={img.url_image}")
                    
                    response_data = ProduitSerializer(produit_complet).data
                    logger.info(f"📤 Réponse API finale: {response_data}")
                    
                    return Response(response_data, status=status.HTTP_201_CREATED)
                else:
                    logger.error(f"❌ Erreurs validation produit: {produit_serializer.errors}")
                    return Response(produit_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    
        except Exception as e:
            logger.error(f"❌ Erreur lors de la création complète: {str(e)}")
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return Response(
                {'error': f'Erreur serveur: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def add_image(self, request, pk=None):
        """Ajouter une image à un produit existant"""
        produit = self.get_object()
        
        data = request.data.copy()
        data['produit'] = produit.id
        
        serializer = ImageProduitSerializer(data=data)
        if serializer.is_valid():
            # Si c'est marqué comme principale, retirer le flag des autres
            if data.get('est_principale', False):
                ImageProduit.objects.filter(produit=produit, est_principale=True).update(est_principale=False)
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_specification(self, request, pk=None):
        """Ajouter une spécification à un produit existant"""
        produit = self.get_object()
        
        data = request.data.copy()
        data['produit'] = produit.id
        
        serializer = SpecificationProduitSerializer(data=data)
        if serializer.is_valid():
            # Si c'est marqué comme défaut, retirer le flag des autres
            if data.get('est_defaut', False):
                SpecificationProduit.objects.filter(produit=produit, est_defaut=True).update(est_defaut=False)
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def images(self, request, pk=None):
        """Récupérer toutes les images d'un produit"""
        produit = self.get_object()
        images = produit.imageproduit_set.all().order_by('ordre', '-est_principale')
        serializer = ImageProduitSerializer(images, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def specifications(self, request, pk=None):
        """Récupérer toutes les spécifications d'un produit"""
        produit = self.get_object()
        specs = produit.specificationproduit_set.all().order_by('-est_defaut')
        serializer = SpecificationProduitSerializer(specs, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        # Temporaire : associer au premier commerçant trouvé
        from .models import DetailsCommercant
        commercant = DetailsCommercant.objects.first()
        if commercant:
            serializer.save(commercant=commercant)
        else:
            serializer.save()


class ImageProduitViewSet(viewsets.ModelViewSet):
    queryset = ImageProduit.objects.all()
    serializer_class = ImageProduitSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ImageProduit.objects.select_related('produit').order_by('produit', 'ordre')


class SpecificationProduitViewSet(viewsets.ModelViewSet):
    queryset = SpecificationProduit.objects.all()
    serializer_class = SpecificationProduitSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return SpecificationProduit.objects.select_related('produit').order_by('produit', '-est_defaut')


class MouvementStockViewSet(viewsets.ModelViewSet):
    queryset = MouvementStock.objects.all()
    serializer_class = MouvementStockSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        mouvement = serializer.save()
        spec = mouvement.specification
        if mouvement.type_mouvement == 'entree':
            spec.quantite_stock += mouvement.quantite
        elif mouvement.type_mouvement == 'sortie':
            if spec.quantite_stock < mouvement.quantite:
                raise serializers.ValidationError("Stock insuffisant pour ce mouvement de sortie")
            spec.quantite_stock -= mouvement.quantite
        spec.save()


class CategorieViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes = [AllowAny]


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().order_by('-date_notification')
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrage possible par query params (ex: ?est_lue=true)
        est_lue = self.request.query_params.get('est_lue')
        if est_lue is not None:
            if est_lue.lower() in ['true', '1']:
                queryset = queryset.filter(est_lue=True)
            elif est_lue.lower() in ['false', '0']:
                queryset = queryset.filter(est_lue=False)
        return queryset


class CommandeViewSet(viewsets.ModelViewSet):
    queryset = Commande.objects.all().order_by('-date_commande')
    serializer_class = CommandeSerializer
    permission_classes = [AllowAny]


class DetailCommandeViewSet(viewsets.ModelViewSet):
    queryset = DetailCommande.objects.all()
    serializer_class = DetailCommandeSerializer
    permission_classes = [AllowAny]


# ===========================
# FONCTIONS UTILITAIRES
# ===========================

@csrf_exempt
@api_view(['POST'])
def upload_image(request):
    """Upload une image et retourne son URL - VERSION FINALE"""
    try:
        print(f"🔍 Méthode: {request.method}")
        print(f"🔍 Headers: {dict(request.headers)}")
        print(f"🔍 Files: {list(request.FILES.keys())}")
        
        if 'image' not in request.FILES:
            return Response({
                'error': 'Aucune image fournie'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        image_file = request.FILES['image']
        print(f"📸 Fichier reçu: {image_file.name}, Taille: {image_file.size}")
        
        # Validation du fichier
        if not image_file.content_type.startswith('image/'):
            return Response({
                'error': 'Le fichier doit être une image'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Taille max 5MB
        if image_file.size > 5 * 1024 * 1024:
            return Response({
                'error': 'Fichier trop volumineux (max 5MB)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Générer un nom unique
        extension = image_file.name.split('.')[-1].lower()
        unique_filename = f"{uuid.uuid4()}.{extension}"
        
        # Créer le dossier uploads s'il n'existe pas
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', 'images')
        os.makedirs(upload_dir, exist_ok=True)
        print(f"📁 Dossier upload: {upload_dir}")
        
        # Chemin relatif pour BDD
        relative_path = os.path.join('uploads', 'images', unique_filename)
        
        # Chemin absolu pour sauvegarder
        absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)
        
        # Sauvegarder le fichier
        with open(absolute_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)
        
        # Construire l'URL correcte
        base_url = f"{request.scheme}://{request.get_host()}"
        image_url = f"{base_url}{settings.MEDIA_URL}{relative_path.replace(os.path.sep, '/')}"
        
        print(f"✅ Image sauvée: {absolute_path}")
        print(f"🔗 URL générée: {image_url}")
        print(f"📁 Fichier existe: {os.path.exists(absolute_path)}")
        
        return Response({
            'success': True,
            'url': image_url,
            'filename': unique_filename,
            'path': relative_path,
            'size': image_file.size
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"❌ Erreur upload: {str(e)}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        return Response({
            'error': f'Erreur serveur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===========================
# FONCTIONS DE DEBUG
# ===========================

@csrf_exempt
def debug_products(request):
    """Fonction de debug pour vérifier les produits et images"""
    try:
        products_data = []
        for product in Produit.objects.all():
            images = product.imageproduit_set.all()
            product_info = {
                'id': product.id,
                'nom': product.nom,
                'images_count': len(images),
                'images': []
            }
            
            for img in images:
                product_info['images'].append({
                    'id': img.id,
                    'url_image': img.url_image,
                    'est_principale': img.est_principale,
                })
            
            products_data.append(product_info)
        
        return JsonResponse({
            'products': products_data,
            'media_url': settings.MEDIA_URL,
            'media_root': str(settings.MEDIA_ROOT),
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)})


@csrf_exempt
def debug_images_complete(request):
    """Diagnostic complet des images et produits"""
    try:
        # 1. Info générale
        total_products = Produit.objects.count()
        total_images = ImageProduit.objects.count()
        
        # 2. Produits détaillés
        products_detail = []
        for product in Produit.objects.all().order_by('-id'):
            images = product.imageproduit_set.all()
            
            # Info produit
            product_info = {
                'id': product.id,
                'nom': product.nom,
                'description': product.description,
                'reference': product.reference,
                'images_count': len(images),
                'images_detail': []
            }
            
            # Détail des images
            for img in images:
                # Vérifier si le fichier existe physiquement
                if img.url_image:
                    # Extraire le chemin relatif de l'URL
                    if img.url_image.startswith('http'):
                        # URL complète: http://10.0.2.2:8000/media/uploads/images/abc.jpg
                        relative_path = img.url_image.split('/media/')[-1] if '/media/' in img.url_image else None
                    else:
                        # Chemin relatif: uploads/images/abc.jpg
                        relative_path = img.url_image
                    
                    # Chemin absolu sur le serveur
                    absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path) if relative_path else None
                    file_exists = os.path.exists(absolute_path) if absolute_path else False
                else:
                    relative_path = None
                    absolute_path = None
                    file_exists = False
                
                image_info = {
                    'id': img.id,
                    'url_image': img.url_image,
                    'est_principale': img.est_principale,
                    'ordre': img.ordre,
                    'date_ajout': img.date_ajout.isoformat(),
                    'relative_path': relative_path,
                    'absolute_path': absolute_path,
                    'file_exists': file_exists,
                }
                product_info['images_detail'].append(image_info)
            
            products_detail.append(product_info)
        
        # 3. Vérifier le dossier uploads
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', 'images')
        upload_dir_exists = os.path.exists(upload_dir)
        
        files_in_upload = []
        if upload_dir_exists:
            try:
                files_in_upload = os.listdir(upload_dir)
            except:
                files_in_upload = ['Erreur lecture dossier']
        
        # 4. Test API produits
        api_products = []
        try:
            for product in Produit.objects.all()[:3]:  # Test sur 3 produits max
                serialized = ProduitSerializer(product)
                api_products.append(serialized.data)
        except Exception as e:
            api_products = [f"Erreur sérialisation: {str(e)}"]
        
        return JsonResponse({
            'summary': {
                'total_products': total_products,
                'total_images': total_images,
                'upload_dir_exists': upload_dir_exists,
                'files_in_upload_count': len(files_in_upload),
            },
            'products_detail': products_detail,
            'upload_directory': {
                'path': upload_dir,
                'exists': upload_dir_exists,
                'files': files_in_upload[:10],  # Max 10 fichiers
            },
            'api_test': api_products,
            'settings': {
                'media_url': settings.MEDIA_URL,
                'media_root': str(settings.MEDIA_ROOT),
            }
        }, indent=2)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)