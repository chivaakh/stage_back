# myapp/views.py - VERSION CORRIGÉE ET NETTOYÉE

import logging
import os
import uuid
import json
import traceback
import requests
from datetime import timedelta
from rest_framework import serializers

# Django core imports
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import transaction
from django.db.models import Q, Avg, Count, Min, Max, Sum, Case, When, IntegerField, CharField, Value
from django.http import JsonResponse
from django.core.mail import send_mail
from django.shortcuts import render
from django.contrib.auth.hashers import make_password, check_password

# Django REST framework imports
from rest_framework import viewsets, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

# Google OAuth
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

# Local models
from .models import (
    Utilisateur, ProfilVendeur, PasswordResetToken,
    Produit, ImageProduit, SpecificationProduit, MouvementStock,
    Categorie, Notification, Commande, DetailCommande, TrackingCommande,
    Panier, Favori, Avis, DetailsClient, DetailsCommercant
)

# Local serializers
from .serializers import (
    ProduitSerializer, CategorieSerializer, ImageProduitSerializer, 
    SpecificationProduitSerializer, SignupSerializer, LoginSerializer,
    PanierSerializer, PanierCreateSerializer, FavoriSerializer,
    CommandeSerializer, DetailCommandeSerializer, TrackingCommandeSerializer,
    NotificationSerializer, AvisSerializer, AvisCreateSerializer,
    ProfilVendeurSerializer, ClientProduitSerializer, ClientCategorieSerializer,
    ClientCommandeSerializer, CommandeCreateSerializer, DetailsClientSerializer,
    MouvementStockSerializer
)

# Logger configuration
logger = logging.getLogger(__name__)

# ===========================
# PAGINATION PERSONNALISÉE
# ===========================

class CustomPagination(PageNumberPagination):
    """Pagination personnalisée"""
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })

# ===========================
# VUES D'AUTHENTIFICATION
# ===========================

class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            # Nettoyer les données : convertir email vide en None
            data = request.data.copy()
            if data.get('email') == '':
                data['email'] = None
                
            serializer = SignupSerializer(data=data, context={'request': request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({"message": "Utilisateur créé avec succès"}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            traceback_str = traceback.format_exc()
            return Response({
                "error": str(e),
                "trace": traceback_str
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

        # Stocker l'id dans la session
        request.session['user_id'] = utilisateur.id_utilisateur

        return Response({"message": "Connexion réussie"}, status=200)

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

        # AMÉLIORATION : Lien générique qui fonctionne pour tous les frontends
        # Au lieu de pointer vers un frontend spécifique, on donne juste le token
        
        # Option 1: Email avec instructions pour utiliser le token
        email_content = f"""
        Bonjour,
        
        Vous avez demandé la réinitialisation de votre mot de passe.
        
        Votre code de réinitialisation est : {token_obj.token}
        
        Pour réinitialiser votre mot de passe :
        - Sur mobile : Ouvrez l'application Ishrili, allez dans "Mot de passe oublié" et saisissez ce code
        - Sur web : Allez sur https://ishrili.com/reset-password et saisissez ce code
        
        Ce code expire dans 1 heure.
        
        Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.
        
        L'équipe Ishrili
        """
        
        # Option 2: Email avec lien universel (pour le futur)
        # reset_url = f"https://ishrili.com/reset-password?token={token_obj.token}"
        
        # Envoyer email avec le contenu adaptatif
        send_mail(
            "Réinitialisation du mot de passe - Ishrili",
            email_content,
            "no-reply@ishrili.com",
            [email],
        )

        return Response({
            "message": "Email envoyé si compte existant", 
            "token": str(token_obj.token)  # AJOUT : Retourner aussi le token pour debug/test
        }, status=200)

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

        # Supprimer le token
        token_obj.delete()

        return Response({"message": "Mot de passe réinitialisé avec succès"}, status=200)

class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "Token requis"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            idinfo = id_token.verify_oauth2_token(
                token, google_requests.Request(), 
                "128897548037-fi6qsoqngat2rg46apt6pq6tfspbfcp3.apps.googleusercontent.com"
            )

            email = idinfo.get("email")
            nom = idinfo.get("family_name") or ""
            prenom = idinfo.get("given_name") or ""
            google_sub = idinfo.get("sub")

            if not email:
                return Response({"error": "Email non trouvé dans le token"}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                telephone_temporaire = f"google_{get_random_string(length=10)}"
                utilisateur, created = Utilisateur.objects.get_or_create(
                    email=email,
                    defaults={
                        "nom": nom,
                        "prenom": prenom,
                        "telephone": telephone_temporaire,
                        "mot_de_passe": make_password(google_sub),
                        "type_utilisateur": "vendeur",
                    },
                )

            request.session['user_id'] = utilisateur.id_utilisateur

            return Response({
                "message": "Connexion Google réussie",
                "user": {
                    "email": utilisateur.email,
                    "nom": utilisateur.nom,
                    "prenom": utilisateur.prenom,
                }
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            logger.error(f"Erreur Google token: {e}")
            return Response({"error": f"Token invalide : {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class FacebookLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        access_token = request.data.get("access_token")
        email = request.data.get("email")

        if not access_token or not email:
            return Response({"error": "Token et email requis"}, status=status.HTTP_400_BAD_REQUEST)

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
            utilisateur.nom = name.split(" ")[-1]
            utilisateur.prenom = " ".join(name.split(" ")[:-1])
            if not utilisateur.telephone:
                utilisateur.telephone = ""
            utilisateur.mot_de_passe = make_password(email)
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


@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        request.session.flush()  # Supprime toutes les données de session (y compris user_id)
        return JsonResponse({'message': 'Déconnexion réussie'}, status=200)
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
# ===========================
# VUES PROFIL VENDEUR
# ===========================

class CreerProfilVendeurView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({"error": "Non connecté."}, status=401)

        try:
            utilisateur = Utilisateur.objects.get(id_utilisateur=user_id)
            profil = utilisateur.profil_vendeur
            serializer = ProfilVendeurSerializer(profil)
            return Response(serializer.data, status=200)
        except Utilisateur.DoesNotExist:
            return Response({"error": "Utilisateur non trouvé."}, status=401)
        except ProfilVendeur.DoesNotExist:
            return Response({"detail": "Profil vendeur introuvable."}, status=404)

    def post(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({"error": "Vous devez être connecté pour créer une boutique."}, status=401)

        try:
            utilisateur = Utilisateur.objects.get(id_utilisateur=user_id)
        except Utilisateur.DoesNotExist:
            return Response({"error": "Utilisateur invalide."}, status=401)

        if utilisateur.type_utilisateur != 'vendeur':
            return Response({"error": "Seuls les vendeurs peuvent créer un profil boutique."}, status=403)

        if hasattr(utilisateur, 'profil_vendeur'):
            return Response({"error": "Le profil vendeur existe déjà."}, status=400)

        serializer = ProfilVendeurSerializer(data=request.data)
        if serializer.is_valid():
            try:
                profil = serializer.save(utilisateur=utilisateur)
                return Response(ProfilVendeurSerializer(profil).data, status=201)
            except Exception as e:
                return Response({
                    "error": "Erreur lors de la création du profil.",
                    "detail": str(e)
                }, status=500)
        else:
            return Response(serializer.errors, status=400)

class VendeurInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({"error": "Non connecté."}, status=401)

        try:
            utilisateur = Utilisateur.objects.get(id_utilisateur=user_id)

            response_data = {
                "id": utilisateur.id_utilisateur,
                "type_utilisateur": utilisateur.type_utilisateur,
                "nom": utilisateur.nom,
                "prenom": utilisateur.prenom,
                "email": utilisateur.email,
                "telephone": utilisateur.telephone,
                "date_creation": utilisateur.date_creation,
                "est_verifie": utilisateur.est_verifie
            }

            if utilisateur.type_utilisateur == 'vendeur':
                try:
                    profil_vendeur = utilisateur.profil_vendeur
                    response_data["boutique"] = {
                        "nom_boutique": profil_vendeur.nom_boutique,
                        "description": profil_vendeur.description,
                        "ville": profil_vendeur.ville,
                        "adresse": profil_vendeur.adresse if hasattr(profil_vendeur, 'adresse') else None,
                        "telephone_professionnel": profil_vendeur.telephone_professionnel if hasattr(profil_vendeur, 'telephone_professionnel') else None,
                        "est_approuve": profil_vendeur.est_approuve,
                        "evaluation": float(profil_vendeur.evaluation),
                        "total_ventes": float(profil_vendeur.total_ventes),
                        "logo": profil_vendeur.logo.url if profil_vendeur.logo else None
                    }
                except ProfilVendeur.DoesNotExist:
                    try:
                        profil_vendeur = ProfilVendeur.objects.get(utilisateur_id=utilisateur.id_utilisateur)
                        response_data["boutique"] = {
                            "nom_boutique": profil_vendeur.nom_boutique,
                            "description": profil_vendeur.description,
                            "ville": profil_vendeur.ville,
                            "adresse": profil_vendeur.adresse if hasattr(profil_vendeur, 'adresse') else None,
                            "telephone_professionnel": profil_vendeur.telephone_professionnel if hasattr(profil_vendeur, 'telephone_professionnel') else None,
                            "est_approuve": profil_vendeur.est_approuve,
                            "evaluation": float(profil_vendeur.evaluation),
                            "total_ventes": float(profil_vendeur.total_ventes),
                            "logo": profil_vendeur.logo.url if profil_vendeur.logo else None
                        }
                    except ProfilVendeur.DoesNotExist:
                        response_data["boutique"] = None
            else:
                response_data["boutique"] = None

            return Response(response_data, status=200)

        except Utilisateur.DoesNotExist:
            return Response({"error": "Utilisateur non trouvé."}, status=401)

# ===========================
# VIEWSETS E-COMMERCE CLIENT
# ===========================

class ClientProduitViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les produits côté client (lecture seule)"""
    serializer_class = ClientProduitSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categorie', 'commercant']
    search_fields = ['nom', 'description', 'reference']
    ordering_fields = ['nom', 'id']
    ordering = ['nom']

    def get_queryset(self):
        return Produit.objects.prefetch_related(
            'imageproduit_set', 'specificationproduit_set', 'avis_set'
        ).select_related('categorie', 'commercant').filter(
            specificationproduit__quantite_stock__gt=0
        ).distinct()

    @action(detail=False, methods=['get'])
    def recherche(self, request):
        """Recherche avancée de produits"""
        query = request.query_params.get('q', '')
        prix_min = request.query_params.get('prix_min')
        prix_max = request.query_params.get('prix_max')
        categorie_id = request.query_params.get('categorie')
        
        queryset = self.get_queryset()
        
        if query:
            queryset = queryset.filter(
                Q(nom__icontains=query) | 
                Q(description__icontains=query) |
                Q(reference__icontains=query)
            )
        
        if prix_min:
            queryset = queryset.filter(specificationproduit__prix__gte=prix_min)
        
        if prix_max:
            queryset = queryset.filter(specificationproduit__prix__lte=prix_max)
        
        if categorie_id:
            queryset = queryset.filter(categorie_id=categorie_id)
        
        page = self.paginate_queryset(queryset.distinct())
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset.distinct(), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def nouveaute(self, request):
        """Récupère les nouveaux produits (derniers 30 jours)"""
        queryset = self.get_queryset().order_by('-id')[:20]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def populaires(self, request):
        """Récupère les produits populaires (plus d'avis)"""
        queryset = self.get_queryset().annotate(
            nb_avis=Count('avis')
        ).filter(nb_avis__gt=0).order_by('-nb_avis')[:20]
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def avis(self, request, pk=None):
        """Récupère tous les avis d'un produit"""
        produit = self.get_object()
        avis = Avis.objects.filter(produit=produit).order_by('-date_creation')
        serializer = AvisSerializer(avis, many=True)
        return Response(serializer.data)

class ClientCategorieViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les catégories côté client"""
    queryset = Categorie.objects.all()
    serializer_class = ClientCategorieSerializer
    permission_classes = [AllowAny]
    
    @action(detail=True, methods=['get'])
    def produits(self, request, pk=None):
        """Récupère tous les produits d'une catégorie"""
        categorie = self.get_object()
        produits = Produit.objects.filter(categorie=categorie).prefetch_related(
            'imageproduit_set', 'specificationproduit_set'
        )
        
        page = self.paginate_queryset(produits)
        if page is not None:
            serializer = ClientProduitSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ClientProduitSerializer(produits, many=True)
        return Response(serializer.data)

# Ajoutez cette correction à votre PanierViewSet dans views.py

class PanierViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion du panier - VERSION CORRIGÉE"""
    serializer_class = PanierSerializer
    permission_classes = [AllowAny]  # TEMPORAIRE
    
    def get_queryset(self):
        """Récupérer les articles du panier du premier client disponible"""
        try:
            client = DetailsClient.objects.first()
            if not client:
                return Panier.objects.none()
            
            return Panier.objects.filter(client=client).select_related(
                'specification', 'specification__produit'
            ).prefetch_related('specification__produit__imageproduit_set')
        except Exception as e:
            logger.error(f"Erreur get_queryset panier: {str(e)}")
            return Panier.objects.none()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PanierCreateSerializer
        return PanierSerializer
    
    def perform_create(self, serializer):
        """Ajouter un produit au panier"""
        try:
            client = DetailsClient.objects.first()
            if not client:
                # Créer un client par défaut temporaire
                client = DetailsClient.objects.create(
                    utilisateur_id=1,  # Utilisateur par défaut
                    nom="Client",
                    prenom="Test",
                    adresse="Adresse test",
                    ville="Nouakchott", 
                    code_postal="00000",
                    pays="Mauritanie"
                )
                logger.info(f"Client temporaire créé: {client.id}")
                
            specification = serializer.validated_data['specification']
            quantite = serializer.validated_data['quantite']
            
            panier_existant = Panier.objects.filter(
                client=client, 
                specification=specification
            ).first()
            
            if panier_existant:
                nouvelle_quantite = panier_existant.quantite + quantite
                
                if nouvelle_quantite > specification.quantite_stock:
                    raise Exception(
                        f"Stock insuffisant. Disponible: {specification.quantite_stock}, "
                        f"déjà dans panier: {panier_existant.quantite}"
                    )
                
                panier_existant.quantite = nouvelle_quantite
                panier_existant.save()
                return panier_existant
            else:
                return serializer.save(client=client)
                
        except Exception as e:
            logger.error(f"Erreur ajout panier: {str(e)}")
            raise Exception(f"Erreur lors de l'ajout au panier: {str(e)}")
    
    @action(detail=False, methods=['post'])
    def ajouter_rapide(self, request):
        """Ajouter rapidement un produit avec sa spécification par défaut - VERSION CORRIGÉE"""
        try:
            produit_id = request.data.get('produit_id')
            quantite = request.data.get('quantite', 1)
            
            logger.info(f"🛒 Tentative ajout produit {produit_id}, quantité {quantite}")
            
            if not produit_id:
                return Response(
                    {'error': 'ID produit requis', 'success': False}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Vérifier si le produit existe
            try:
                produit = Produit.objects.get(id=produit_id)
                logger.info(f"Produit trouvé: {produit.nom}")
            except Produit.DoesNotExist:
                return Response(
                    {'error': f'Produit avec ID {produit_id} non trouvé', 'success': False}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Récupérer ou créer un client
            client = DetailsClient.objects.first()
            if not client:
                # Créer un utilisateur et client temporaires
                try:
                    utilisateur = Utilisateur.objects.create(
                        telephone="temp_user",
                        nom="Client",
                        prenom="Temporaire",
                        type_utilisateur="client",
                        mot_de_passe="temp_password"
                    )
                    client = DetailsClient.objects.create(
                        utilisateur=utilisateur,
                        nom="Client",
                        prenom="Temporaire",
                        adresse="Adresse temporaire",
                        ville="Nouakchott",
                        code_postal="00000",
                        pays="Mauritanie"
                    )
                    logger.info(f"Client temporaire créé: {client.nom} {client.prenom} (ID: {client.id})")
                except Exception as e:
                    logger.error(f"Erreur création client: {str(e)}")
                    return Response(
                        {'error': 'Erreur lors de la création du client temporaire', 'success': False}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            logger.info(f"Client trouvé/créé: {client.nom} {client.prenom} (ID: {client.id})")
            
            # Trouver la spécification par défaut du produit
            specification = SpecificationProduit.objects.filter(
                produit_id=produit_id, 
                est_defaut=True
            ).first()
            
            if not specification:
                specification = SpecificationProduit.objects.filter(
                    produit_id=produit_id
                ).first()
            
            if not specification:
                return Response(
                    {'error': f'Aucune spécification trouvée pour le produit {produit_id}', 'success': False}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            logger.info(f"Spécification trouvée: {specification.nom} (ID: {specification.id}, Stock: {specification.quantite_stock})")
            
            # Vérifier le stock
            if specification.quantite_stock <= 0:
                return Response(
                    {'error': 'Produit en rupture de stock', 'success': False}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Vérifier si déjà dans le panier
            panier_existant = Panier.objects.filter(
                client=client, 
                specification=specification
            ).first()
            
            if panier_existant:
                nouvelle_quantite = panier_existant.quantite + quantite
                
                if nouvelle_quantite > specification.quantite_stock:
                    return Response(
                        {
                            'error': f'Stock insuffisant. Disponible: {specification.quantite_stock}, déjà dans panier: {panier_existant.quantite}', 
                            'success': False
                        }, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                panier_existant.quantite = nouvelle_quantite
                panier_existant.save()
                instance = panier_existant
                logger.info(f"Quantité mise à jour: {instance.quantite}")
            else:
                if quantite > specification.quantite_stock:
                    return Response(
                        {
                            'error': f'Quantité demandée ({quantite}) supérieure au stock disponible ({specification.quantite_stock})', 
                            'success': False
                        }, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                instance = Panier.objects.create(
                    client=client,
                    specification=specification,
                    quantite=quantite
                )
                logger.info(f"Nouvel article créé: {instance.id}")
            
            return Response(
                {
                    'message': 'Produit ajouté au panier avec succès', 
                    'success': True,
                    'item': PanierSerializer(instance).data
                },
                status=status.HTTP_201_CREATED
            )
                
        except Exception as e:
            logger.error(f"❌ Erreur ajout rapide panier: {str(e)}")
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return Response(
                {'error': f'Erreur lors de l\'ajout: {str(e)}', 'success': False}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def resume(self, request):
        """Récupère le résumé du panier"""
        try:
            client = DetailsClient.objects.first()
            if not client:
                return Response({
                    'total_items': 0,
                    'total_prix': 0.0,
                    'nombre_articles': 0,
                    'articles': []
                })
                
            panier_items = self.get_queryset()
            
            total_items = sum(item.quantite for item in panier_items)
            total_prix = sum(
                (item.specification.prix_promo or item.specification.prix) * item.quantite 
                for item in panier_items
            )
            
            return Response({
                'total_items': total_items,
                'total_prix': float(total_prix),
                'nombre_articles': panier_items.count(),
                'articles': PanierSerializer(panier_items, many=True).data
            })
        except Exception as e:
            logger.error(f"Erreur résumé panier: {str(e)}")
            return Response({
                'total_items': 0,
                'total_prix': 0.0,
                'nombre_articles': 0,
                'articles': []
            })
    
    @action(detail=False, methods=['post'])
    def vider(self, request):
        """Vide complètement le panier"""
        try:
            client = DetailsClient.objects.first()
            if not client:
                return Response(
                    {'error': 'Client non trouvé', 'success': False}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            count = Panier.objects.filter(client=client).count()
            Panier.objects.filter(client=client).delete()
            return Response({
                'message': f'{count} articles supprimés du panier',
                'success': True
            })
        except Exception as e:
            logger.error(f"Erreur vidage panier: {str(e)}")
            return Response(
                {'error': 'Erreur lors du vidage du panier', 'success': False}, 
                status=status.HTTP_400_BAD_REQUEST
            )

# ===========================
# VIEWSETS PRODUITS VENDEUR
# ===========================

def get_current_vendor(request):
    """
    ✅ FONCTION UTILITAIRE : Récupère le vendeur connecté depuis la session
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return None, "Vous devez être connecté"
    
    try:
        utilisateur = Utilisateur.objects.get(id_utilisateur=user_id)
        
        if utilisateur.type_utilisateur != 'vendeur':
            return None, "Seuls les vendeurs peuvent accéder à cette ressource"
        
        try:
            profil_vendeur = utilisateur.profil_vendeur
            return profil_vendeur, None
        except ProfilVendeur.DoesNotExist:
            return None, "Profil vendeur introuvable"
            
    except Utilisateur.DoesNotExist:
        return None, "Utilisateur introuvable"

def require_vendor_permission(view_func):
    """
    ✅ DÉCORATEUR : S'assurer qu'un vendeur ne peut agir que sur ses produits
    """
    def wrapper(view_instance, request, *args, **kwargs):
        # Pour les méthodes qui modifient un produit existant
        if hasattr(view_instance, 'get_object'):
            try:
                obj = view_instance.get_object()
                vendor, error = get_current_vendor(request)
                
                if error:
                    return Response({'error': error}, status=status.HTTP_401_UNAUTHORIZED)
                
                if hasattr(obj, 'vendeur') and obj.vendeur != vendor:
                    return Response(
                        {'error': 'Vous ne pouvez modifier que vos propres produits'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            except:
                pass
        
        return view_func(view_instance, request, *args, **kwargs)
    return wrapper

# ---------------------------
# DÉCORATEUR ALTERNATIF POUR LES MÉTHODES DE CLASSE
# ---------------------------

from functools import wraps

def vendor_required(f):
    """
    ✅ DÉCORATEUR : Vérifier qu'un vendeur est connecté
    """
    @wraps(f)
    def decorated_function(self, request, *args, **kwargs):
        vendor, error = get_current_vendor(request)
        if error:
            return Response({'error': error}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Ajouter le vendeur à la request pour usage dans la méthode
        request.current_vendor = vendor
        return f(self, request, *args, **kwargs)
    
    return decorated_function



# Modifier ProduitViewSet
class ProduitViewSet(viewsets.ModelViewSet):
    serializer_class = ProduitSerializer
    permission_classes = [AllowAny]  # ✅ À changer en IsAuthenticated en production

    def get_queryset(self):
        """✅ NOUVEAU : Filtrer les produits selon le vendeur connecté"""
        # Obtenir l'ID utilisateur de la session
        user_id = self.request.session.get('user_id')
        
        if not user_id:
            # Si pas connecté, retourner queryset vide
            return Produit.objects.none()
        
        try:
            # Obtenir l'utilisateur connecté
            utilisateur = Utilisateur.objects.get(id_utilisateur=user_id)
            
            # Vérifier que c'est un vendeur
            if utilisateur.type_utilisateur != 'vendeur':
                return Produit.objects.none()
            
            # Obtenir le profil vendeur
            profil_vendeur = utilisateur.profil_vendeur
            
            # ✅ FILTRER : Retourner seulement les produits de ce vendeur
            return Produit.objects.filter(
                vendeur=profil_vendeur
            ).prefetch_related(
                'imageproduit_set', 'specificationproduit_set'
            ).select_related('commercant', 'categorie', 'vendeur')
            
        except (Utilisateur.DoesNotExist, ProfilVendeur.DoesNotExist):
            return Produit.objects.none()

    def perform_create(self, serializer):
        """✅ NOUVEAU : Associer automatiquement le produit au vendeur connecté"""
        user_id = self.request.session.get('user_id')
        
        if not user_id:
            raise serializers.ValidationError("Vous devez être connecté pour créer un produit")
        
        try:
            utilisateur = Utilisateur.objects.get(id_utilisateur=user_id)
            
            if utilisateur.type_utilisateur != 'vendeur':
                raise serializers.ValidationError("Seuls les vendeurs peuvent créer des produits")
            
            profil_vendeur = utilisateur.profil_vendeur
            
            # ✅ ASSOCIER automatiquement au vendeur connecté
            serializer.save(vendeur=profil_vendeur)
            
        except (Utilisateur.DoesNotExist, ProfilVendeur.DoesNotExist):
            raise serializers.ValidationError("Profil vendeur introuvable")

    def perform_update(self, serializer):
        """✅ NOUVEAU : S'assurer qu'un vendeur ne peut modifier que ses produits"""
        user_id = self.request.session.get('user_id')
        
        if not user_id:
            raise serializers.ValidationError("Vous devez être connecté")
        
        try:
            utilisateur = Utilisateur.objects.get(id_utilisateur=user_id)
            profil_vendeur = utilisateur.profil_vendeur
            
            # Vérifier que le produit appartient bien au vendeur connecté
            if serializer.instance.vendeur != profil_vendeur:
                raise serializers.ValidationError("Vous ne pouvez modifier que vos propres produits")
            
            serializer.save()
            
        except (Utilisateur.DoesNotExist, ProfilVendeur.DoesNotExist):
            raise serializers.ValidationError("Profil vendeur introuvable")

    def perform_destroy(self, instance):
        """✅ NOUVEAU : S'assurer qu'un vendeur ne peut supprimer que ses produits"""
        user_id = self.request.session.get('user_id')
        
        if not user_id:
            raise serializers.ValidationError("Vous devez être connecté")
        
        try:
            utilisateur = Utilisateur.objects.get(id_utilisateur=user_id)
            profil_vendeur = utilisateur.profil_vendeur
            
            # Vérifier que le produit appartient bien au vendeur connecté
            if instance.vendeur != profil_vendeur:
                raise serializers.ValidationError("Vous ne pouvez supprimer que vos propres produits")
            
            instance.delete()
            
        except (Utilisateur.DoesNotExist, ProfilVendeur.DoesNotExist):
            raise serializers.ValidationError("Profil vendeur introuvable")

    def create(self, request, *args, **kwargs):
        """✅ MODIFIÉ : Créer un produit avec vérification vendeur"""
        logger.info(f"🔍 Création produit par user_id: {request.session.get('user_id')}")
        
        try:
            with transaction.atomic():
                # 1. Vérifier l'authentification
                user_id = request.session.get('user_id')
                if not user_id:
                    return Response(
                        {'error': 'Vous devez être connecté pour créer un produit'}, 
                        status=status.HTTP_401_UNAUTHORIZED
                    )
                
                # 2. Vérifier le profil vendeur
                try:
                    utilisateur = Utilisateur.objects.get(id_utilisateur=user_id)
                    if utilisateur.type_utilisateur != 'vendeur':
                        return Response(
                            {'error': 'Seuls les vendeurs peuvent créer des produits'}, 
                            status=status.HTTP_403_FORBIDDEN
                        )
                    profil_vendeur = utilisateur.profil_vendeur
                except (Utilisateur.DoesNotExist, ProfilVendeur.DoesNotExist):
                    return Response(
                        {'error': 'Profil vendeur introuvable'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # 3. Extraire les données
                produit_data = {
                    'nom': request.data.get('nom'),
                    'description': request.data.get('description'),
                    'reference': request.data.get('reference'),
                }
                
                if request.data.get('categorie'):
                    produit_data['categorie_id'] = request.data.get('categorie')

                
                images_data = request.data.get('images', [])
                specifications_data = request.data.get('specifications', [])
                
                logger.info(f"📦 Produit pour vendeur: {profil_vendeur.nom_boutique}")
                
                # 4. Créer le produit avec vendeur
                produit_serializer = ProduitSerializer(data=produit_data)
                if produit_serializer.is_valid():
                    # ✅ ASSOCIER au vendeur connecté
                    produit = produit_serializer.save(vendeur=profil_vendeur)
                    logger.info(f"✅ Produit créé avec ID: {produit.id} pour vendeur: {profil_vendeur.nom_boutique}")
                    
                    # 5. Ajouter les images et spécifications (code existant)
                    images_creees = 0
                    for i, image_data in enumerate(images_data):
                        if image_data.get('url_image'):
                            try:
                                image_obj = ImageProduit.objects.create(
                                    produit=produit,
                                    url_image=image_data['url_image'],
                                    est_principale=image_data.get('est_principale', False),
                                    ordre=image_data.get('ordre', i)
                                )
                                images_creees += 1
                                logger.info(f"✅ Image {i+1} créée: ID={image_obj.id}")
                            except Exception as e:
                                logger.error(f"❌ Erreur création image {i+1}: {str(e)}")
                    
                    specs_creees = 0
                    for spec_data in specifications_data:
                        if spec_data.get('nom') and spec_data.get('prix'):
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
                    
                    # 6. Retourner le produit complet
                    produit_complet = self.get_queryset().get(id=produit.id)
                    response_data = ProduitSerializer(produit_complet).data
                    
                    logger.info(f"📤 Produit créé avec succès: {produit.nom} pour {profil_vendeur.nom_boutique}")
                    return Response(response_data, status=status.HTTP_201_CREATED)
                    
                else:
                    logger.error(f"❌ Erreurs validation produit: {produit_serializer.errors}")
                    return Response(produit_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    
        except Exception as e:
            logger.error(f"❌ Erreur lors de la création: {str(e)}")
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




class VendorAuthMiddleware:
    """
    ✅ MIDDLEWARE : Pour débugger l'authentification vendeur
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log de la session pour debug
        user_id = request.session.get('user_id')
        if user_id and request.path.startswith('/api/'):
            try:
                user = Utilisateur.objects.get(id_utilisateur=user_id)
                print(f"🔍 User connecté: {user.nom} ({user.type_utilisateur})")
                
                if user.type_utilisateur == 'vendeur':
                    try:
                        vendor = user.profil_vendeur
                        print(f"🏪 Boutique: {vendor.nom_boutique}")
                    except ProfilVendeur.DoesNotExist:
                        print("❌ Pas de profil vendeur")
                        
            except Utilisateur.DoesNotExist:
                print(f"❌ User ID {user_id} introuvable")
        
        response = self.get_response(request)
        return response



@csrf_exempt
def vendor_products_debug(request):
    """
    ✅ VUE DE DEBUG : Vérifier que chaque vendeur voit bien ses produits
    """
    try:
        # Obtenir tous les vendeurs
        vendeurs = ProfilVendeur.objects.all()
        debug_info = {
            'total_vendeurs': vendeurs.count(),
            'total_produits': Produit.objects.count(),
            'vendeurs_detail': []
        }
        
        for vendeur in vendeurs:
            produits_vendeur = Produit.objects.filter(vendeur=vendeur)
            vendeur_info = {
                'id': vendeur.id,
                'nom_boutique': vendeur.nom_boutique,
                'ville': vendeur.ville,
                'utilisateur_id': vendeur.utilisateur.id_utilisateur,
                'nombre_produits': produits_vendeur.count(),
                'produits': []
            }
            
            for produit in produits_vendeur:
                vendeur_info['produits'].append({
                    'id': produit.id,
                    'nom': produit.nom,
                    'reference': produit.reference,
                    'vendeur_nom': produit.vendeur.nom_boutique if produit.vendeur else None
                })
            
            debug_info['vendeurs_detail'].append(vendeur_info)
        
        # Produits sans vendeur
        produits_orphelins = Produit.objects.filter(vendeur__isnull=True)
        debug_info['produits_sans_vendeur'] = {
            'count': produits_orphelins.count(),
            'produits': [
                {
                    'id': p.id,
                    'nom': p.nom,
                    'reference': p.reference
                } for p in produits_orphelins
            ]
        }
        
        return JsonResponse(debug_info, indent=2)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)

@csrf_exempt 
def current_vendor_info(request):
    """
    ✅ VUE DE DEBUG : Informations sur le vendeur connecté
    """
    try:
        user_id = request.session.get('user_id')
        
        if not user_id:
            return JsonResponse({
                'connected': False,
                'error': 'Aucun utilisateur connecté'
            })
        
        try:
            utilisateur = Utilisateur.objects.get(id_utilisateur=user_id)
            
            info = {
                'connected': True,
                'user_id': user_id,
                'nom': utilisateur.nom,
                'prenom': utilisateur.prenom,
                'email': utilisateur.email,
                'telephone': utilisateur.telephone,
                'type_utilisateur': utilisateur.type_utilisateur,
                'est_vendeur': utilisateur.type_utilisateur == 'vendeur'
            }
            
            if utilisateur.type_utilisateur == 'vendeur':
                try:
                    profil_vendeur = utilisateur.profil_vendeur
                    info['boutique'] = {
                        'id': profil_vendeur.id,
                        'nom_boutique': profil_vendeur.nom_boutique,
                        'ville': profil_vendeur.ville,
                        'est_approuve': profil_vendeur.est_approuve
                    }
                    
                    # Compter les produits de ce vendeur
                    produits_count = Produit.objects.filter(vendeur=profil_vendeur).count()
                    info['boutique']['nombre_produits'] = produits_count
                    
                except ProfilVendeur.DoesNotExist:
                    info['boutique'] = None
                    info['error'] = 'Profil vendeur introuvable'
            
            return JsonResponse(info)
            
        except Utilisateur.DoesNotExist:
            return JsonResponse({
                'connected': False,
                'error': f'Utilisateur {user_id} introuvable'
            })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)

class VendorStatsView(APIView):
    """
    ✅ VUE API : Statistiques du vendeur connecté
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        vendor, error = get_current_vendor(request)
        if error:
            return Response({'error': error}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            # Statistiques des produits du vendeur
            produits = Produit.objects.filter(vendeur=vendor)
            
            stats = {
                'boutique': {
                    'nom': vendor.nom_boutique,
                    'ville': vendor.ville,
                    'est_approuve': vendor.est_approuve,
                    'evaluation': float(vendor.evaluation),
                    'total_ventes': float(vendor.total_ventes)
                },
                'produits': {
                    'total': produits.count(),
                    'en_stock': 0,
                    'rupture_stock': 0,
                    'stock_faible': 0
                },
                'categories': {},
                'derniers_produits': []
            }
            
            # Analyser le stock
            for produit in produits:
                stock_total = sum(
                    spec.quantite_stock 
                    for spec in produit.specificationproduit_set.all()
                )
                
                if stock_total == 0:
                    stats['produits']['rupture_stock'] += 1
                elif stock_total <= 5:
                    stats['produits']['stock_faible'] += 1
                else:
                    stats['produits']['en_stock'] += 1
                
                # Compter par catégorie
                if produit.categorie:
                    cat_name = produit.categorie.nom
                    stats['categories'][cat_name] = stats['categories'].get(cat_name, 0) + 1
            
            # Derniers produits créés
            derniers = produits.order_by('-id')[:5]
            for produit in derniers:
                stats['derniers_produits'].append({
                    'id': produit.id,
                    'nom': produit.nom,
                    'reference': produit.reference,
                    'categorie': produit.categorie.nom if produit.categorie else None
                })
            
            return Response(stats)
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors du calcul des statistiques: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )







# À ajouter dans settings.py dans MIDDLEWARE:
# 'myapp.middleware.VendorAuthMiddleware',
# ===========================
# AUTRES VIEWSETS
# ===========================

class CategorieViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all().order_by('nom')
    serializer_class = CategorieSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    
    def get_queryset(self):
        include_empty = self.request.query_params.get('include_empty', 'true')
        queryset = Categorie.objects.all()
        
        if include_empty.lower() == 'false':
            queryset = queryset.filter(produit__isnull=False).distinct()
        
        return queryset.order_by('nom')

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

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().order_by('-date_notification')
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
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
    
    @action(detail=False, methods=['get'])
    def commandes_du_jour(self, request):
        """Récupère les commandes du jour actuel"""
        today = timezone.now().date()
        commandes = Commande.objects.filter(
            date_commande__date=today
        ).order_by('-date_commande')
        
        serializer = self.get_serializer(commandes, many=True)
        return Response({
            'results': serializer.data,
            'count': commandes.count(),
            'date': today.strftime('%Y-%m-%d')
        })
    
    @action(detail=True, methods=['get'])
    def tracking(self, request, pk=None):
        """Récupère l'historique de tracking d'une commande"""
        try:
            commande = self.get_object()
            
            tracking_entries = TrackingCommande.objects.filter(
                commande=commande
            ).order_by('-date_modification')
            
            if not tracking_entries.exists():
                TrackingCommande.objects.create(
                    commande=commande,
                    ancien_statut=None,
                    nouveau_statut=commande.statut
                )
                tracking_entries = TrackingCommande.objects.filter(
                    commande=commande
                ).order_by('-date_modification')
            
            tracking_data = []
            for entry in tracking_entries:
                tracking_data.append({
                    'ancien_statut': entry.ancien_statut,
                    'nouveau_statut': entry.nouveau_statut,
                    'date_modification': entry.date_modification.isoformat(),
                })
            
            return Response(tracking_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Erreur tracking commande {pk}: {str(e)}")
            return Response(
                {'error': f'Erreur lors de la récupération du tracking: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DetailCommandeViewSet(viewsets.ModelViewSet):
    queryset = DetailCommande.objects.all()
    serializer_class = DetailCommandeSerializer
    permission_classes = [AllowAny]

class FavoriViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des favoris - VERSION DEBUG"""
    serializer_class = FavoriSerializer
    permission_classes = [AllowAny]  # ⚠️ TEMPORAIRE - pour tests uniquement
    
    def get_queryset(self):
        """Récupérer les favoris du premier client disponible"""
        try:
            # TEMPORAIRE: utiliser le premier client pour les tests
            client = DetailsClient.objects.first()
            if not client:
                logger.warning("❌ Aucun client trouvé dans get_queryset")
                return Favori.objects.none()
            
            queryset = Favori.objects.filter(client=client).select_related(
                'produit', 'produit__categorie'
            ).prefetch_related('produit__imageproduit_set')
            
            logger.info(f"✅ get_queryset: {queryset.count()} favoris trouvés pour client {client.id}")
            return queryset
            
        except Exception as e:
            logger.error(f"❌ Erreur get_queryset favoris: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return Favori.objects.none()
    
    def perform_create(self, serializer):
        """Ajouter un favori"""
        try:
            # TEMPORAIRE: utiliser le premier client
            client = self.get_or_create_test_client()
            
            produit = serializer.validated_data['produit']
            logger.info(f"🔄 Tentative d'ajout favori: client={client.id}, produit={produit.id}")
            
            # Vérifier si déjà en favoris
            if Favori.objects.filter(client=client, produit=produit).exists():
                logger.warning(f"⚠️ Produit {produit.id} déjà en favoris pour client {client.id}")
                raise Exception("Produit déjà dans les favoris")
            
            # Sauvegarder
            favori = serializer.save(client=client)
            logger.info(f"✅ Favori créé avec succès: ID={favori.id}")
            
        except Exception as e:
            logger.error(f"❌ Erreur ajout favori: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise Exception(f"Erreur lors de l'ajout aux favoris: {str(e)}")
    
    def get_or_create_test_client(self):
        """Obtenir ou créer un client pour les tests"""
        # Essayer de récupérer le premier client
        client = DetailsClient.objects.first()
        
        if client:
            logger.info(f"✅ Client existant trouvé: {client.id}")
            return client
        
        # Créer un client temporaire
        logger.warning("⚠️ Aucun client trouvé, création d'un client temporaire")
        
        utilisateur = Utilisateur.objects.first()
        if not utilisateur:
            logger.error("❌ Aucun utilisateur disponible pour créer un client")
            raise Exception("Aucun utilisateur disponible")
        
        client = DetailsClient.objects.create(
            utilisateur=utilisateur,
            nom="Client",
            prenom="Test",
            adresse="Adresse test",
            ville="Nouakchott",
            code_postal="00000",
            pays="Mauritanie"
        )
        logger.info(f"✅ Client temporaire créé: {client.id}")
        return client
    
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """Toggle favori avec debug complet"""
        logger.info(f"🔄 [TOGGLE] Début - Data reçue: {request.data}")
        
        try:
            # 1. Validation des données d'entrée
            produit_id = request.data.get('produit_id')
            if not produit_id:
                logger.error("❌ [TOGGLE] produit_id manquant")
                return Response(
                    {'error': 'produit_id requis', 'success': False}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            logger.info(f"🔍 [TOGGLE] Produit ID reçu: {produit_id} (type: {type(produit_id)})")
            
            # 2. Vérifier si le produit existe
            try:
                produit = Produit.objects.get(id=produit_id)
                logger.info(f"✅ [TOGGLE] Produit trouvé: {produit.nom} (ID: {produit.id})")
            except Produit.DoesNotExist:
                logger.error(f"❌ [TOGGLE] Produit {produit_id} non trouvé")
                return Response(
                    {'error': 'Produit non trouvé', 'success': False}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 3. Obtenir ou créer le client
            try:
                client = self.get_or_create_test_client()
                logger.info(f"✅ [TOGGLE] Client obtenu: {client.id}")
            except Exception as e:
                logger.error(f"❌ [TOGGLE] Erreur client: {str(e)}")
                return Response(
                    {'error': f'Erreur client: {str(e)}', 'success': False}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 4. Toggle logic avec transaction
            with transaction.atomic():
                favori = Favori.objects.filter(client=client, produit=produit).first()
                
                if favori:
                    # Retirer des favoris
                    logger.info(f"🗑️ [TOGGLE] Suppression favori ID: {favori.id}")
                    favori.delete()
                    message = 'Retiré des favoris'
                    is_favori = False
                    
                else:
                    # Ajouter aux favoris
                    logger.info(f"➕ [TOGGLE] Création nouveau favori")
                    favori = Favori.objects.create(client=client, produit=produit)
                    logger.info(f"✅ [TOGGLE] Favori créé avec ID: {favori.id}")
                    message = 'Ajouté aux favoris'
                    is_favori = True
            
            # 5. Vérification post-toggle
            favori_count = Favori.objects.filter(client=client).count()
            logger.info(f"📊 [TOGGLE] Total favoris pour client {client.id}: {favori_count}")
            
            # 6. Réponse de succès
            response_data = {
                'message': message,
                'is_favori': is_favori,
                'success': True,
                'debug_info': {  # Informations de debug
                    'client_id': client.id,
                    'produit_id': produit.id,
                    'total_favoris': favori_count
                }
            }
            
            logger.info(f"✅ [TOGGLE] Succès: {response_data}")
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"❌ [TOGGLE] Erreur inattendue: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            return Response(
                {
                    'error': f'Erreur serveur: {str(e)}', 
                    'success': False,
                    'debug_info': {
                        'error_type': type(e).__name__,
                        'error_details': str(e)
                    }
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request, *args, **kwargs):
        """Override list pour debug"""
        logger.info("🔍 [LIST] Début de list favoris")
        
        try:
            queryset = self.get_queryset()
            logger.info(f"✅ [LIST] Queryset obtenu: {queryset.count()} éléments")
            
            serializer = self.get_serializer(queryset, many=True)
            logger.info(f"✅ [LIST] Sérialisation terminée")
            
            response_data = {
                'count': queryset.count(),
                'results': serializer.data
            }
            
            logger.info(f"✅ [LIST] Réponse prête: {len(serializer.data)} favoris")
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"❌ [LIST] Erreur: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            return Response(
                {'error': f'Erreur lors du chargement: {str(e)}', 'results': []},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AvisViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des avis"""
    serializer_class = AvisSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        try:
            client = self.request.user.detailsclient
            return Avis.objects.filter(client=client).select_related('produit')
        except:
            return Avis.objects.none()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AvisCreateSerializer
        return AvisSerializer
    
    def perform_create(self, serializer):
        try:
            client = self.request.user.detailsclient
            produit = serializer.validated_data['produit']
            
            if Avis.objects.filter(client=client, produit=produit).exists():
                raise serializers.ValidationError("Vous avez déjà donné un avis pour ce produit")
            
            serializer.save(client=client)
        except Exception as e:
            raise serializers.ValidationError(str(e))

class ClientCommandeViewSet(viewsets.ModelViewSet):
    """ViewSet pour les commandes côté client"""
    serializer_class = ClientCommandeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        try:
            client = self.request.user.detailsclient
            return Commande.objects.filter(client=client).prefetch_related(
                'detailcommande_set', 
                'detailcommande_set__specification',
                'detailcommande_set__specification__produit'
            ).order_by('-date_commande')
        except:
            return Commande.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CommandeCreateSerializer
        return ClientCommandeSerializer
    
    @action(detail=False, methods=['post'])
    def commander(self, request):
        """Créer une commande depuis le panier"""
        try:
            with transaction.atomic():
                client = request.user.detailsclient
                panier_items = Panier.objects.filter(client=client)
                
                if not panier_items.exists():
                    return Response(
                        {'error': 'Panier vide'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                montant_total = sum(
                    (item.specification.prix_promo or item.specification.prix) * item.quantite 
                    for item in panier_items
                )
                
                commande = Commande.objects.create(
                    client=client,
                    montant_total=montant_total,
                    statut='en_attente'
                )
                
                for item in panier_items:
                    DetailCommande.objects.create(
                        commande=commande,
                        specification=item.specification,
                        quantite=item.quantite,
                        prix_unitaire=item.specification.prix_promo or item.specification.prix
                    )
                    
                    item.specification.quantite_stock -= item.quantite
                    item.specification.save()
                
                panier_items.delete()
                
                return Response(
                    {'message': 'Commande créée avec succès', 'commande_id': commande.id},
                    status=status.HTTP_201_CREATED
                )
                
        except Exception as e:
            logger.error(f"Erreur création commande: {str(e)}")
            return Response(
                {'error': 'Erreur lors de la création de la commande'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ClientProfilViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion du profil client"""
    serializer_class = DetailsClientSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        try:
            return DetailsClient.objects.filter(utilisateur=self.request.user)
        except:
            return DetailsClient.objects.none()
    
    @action(detail=False, methods=['get'])
    def mon_profil(self, request):
        """Récupère le profil du client connecté"""
        try:
            profil = request.user.detailsclient
            serializer = self.get_serializer(profil)
            return Response(serializer.data)
        except:
            return Response(
                {'error': 'Profil client non trouvé'}, 
                status=status.HTTP_404_NOT_FOUND
            )

# ===========================
# FONCTIONS UTILITAIRES
# ===========================

@csrf_exempt
@api_view(['POST'])
def upload_image(request):
    """Upload une image et retourne son URL - VERSION MOBILE COMPATIBLE"""
    try:
        print(f"🔍 Méthode: {request.method}")
        print(f"🔍 Headers: {dict(request.headers)}")
        print(f"🔍 Files: {list(request.FILES.keys())}")
        print(f"🔍 User-Agent: {request.META.get('HTTP_USER_AGENT', 'N/A')}")
        print(f"🔍 Remote Address: {request.META.get('REMOTE_ADDR', 'N/A')}")
        
        if 'image' not in request.FILES:
            return Response({
                'error': 'Aucune image fournie'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        image_file = request.FILES['image']
        print(f"📸 Fichier reçu: {image_file.name}, Taille: {image_file.size}")
        
        if not image_file.content_type.startswith('image/'):
            return Response({
                'error': 'Le fichier doit être une image'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if image_file.size > 5 * 1024 * 1024:
            return Response({
                'error': 'Fichier trop volumineux (max 5MB)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        extension = image_file.name.split('.')[-1].lower()
        unique_filename = f"{uuid.uuid4()}.{extension}"
        
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', 'images')
        os.makedirs(upload_dir, exist_ok=True)
        print(f"📁 Dossier upload: {upload_dir}")
        
        relative_path = os.path.join('uploads', 'images', unique_filename)
        absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)
        
        with open(absolute_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)
        
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        host = request.get_host()
        
        is_flutter_app = 'Dart' in user_agent or 'Flutter' in user_agent
        
        print(f"📱 Flutter app détecté: {is_flutter_app}")
        print(f"🌐 Host: {host}")
        
        if is_flutter_app and ('localhost' in host or '127.0.0.1' in host):
            base_url = f"{request.scheme}://10.0.2.2:8000"
            print(f"📱 URL base mobile: {base_url}")
        else:
            base_url = f"{request.scheme}://{host}"
            print(f"🌐 URL base web: {base_url}")
        
        image_url = f"{base_url}{settings.MEDIA_URL}{relative_path.replace(os.path.sep, '/')}"
        
        print(f"✅ Image sauvée: {absolute_path}")
        print(f"🔗 URL générée: {image_url}")
        print(f"📁 Fichier existe: {os.path.exists(absolute_path)}")
        
        return Response({
            'success': True,
            'url': image_url,
            'filename': unique_filename,
            'path': relative_path,
            'size': image_file.size,
            'debug_info': {
                'is_flutter_app': is_flutter_app,
                'host': host,
                'user_agent': user_agent[:100]
            }
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
        total_products = Produit.objects.count()
        total_images = ImageProduit.objects.count()
        
        products_detail = []
        for product in Produit.objects.all().order_by('-id'):
            images = product.imageproduit_set.all()
            
            product_info = {
                'id': product.id,
                'nom': product.nom,
                'description': product.description,
                'reference': product.reference,
                'images_count': len(images),
                'images_detail': []
            }
            
            for img in images:
                if img.url_image:
                    if img.url_image.startswith('http'):
                        relative_path = img.url_image.split('/media/')[-1] if '/media/' in img.url_image else None
                    else:
                        relative_path = img.url_image
                    
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
        
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', 'images')
        upload_dir_exists = os.path.exists(upload_dir)
        
        files_in_upload = []
        if upload_dir_exists:
            try:
                files_in_upload = os.listdir(upload_dir)
            except:
                files_in_upload = ['Erreur lecture dossier']
        
        api_products = []
        try:
            for product in Produit.objects.all()[:3]:
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
                'files': files_in_upload[:10],
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