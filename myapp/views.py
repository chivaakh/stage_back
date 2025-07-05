# myapp/views.py - VERSION FINALE COMPLÈTE ET CORRIGÉE ✅

from django.utils import timezone
# Imports groupés et organisés
# myapp/views.py - VERSION COMPLÈTE avec tous les ViewSets
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import Produit, ImageProduit, SpecificationProduit, Utilisateur, PasswordResetToken, ProfilVendeur
from .serializers import AvisCreateSerializer, AvisSerializer, ClientCategorieSerializer, ClientCommandeSerializer, CommandeCreateSerializer, FavoriSerializer, PanierSerializer, ProduitSerializer, ImageProduitSerializer, SpecificationProduitSerializer , SignupSerializer, LoginSerializer, ProfilVendeurSerializer
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
from rest_framework.permissions import IsAuthenticated


from .serializers import SignupWithDetailsSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


# Dans views.py - Vue SignupWithDetails corrigée
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.contrib.auth.hashers import make_password
import traceback
import json


from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count
from .models import (
    Produit, Categorie, Panier, Favori, Commande, 
    DetailCommande, Avis, DetailsClient, SpecificationProduit
)
from .serializers import (
    ClientProduitSerializer, 
    ClientCategorieSerializer,
    PanierSerializer, PanierCreateSerializer, 
    FavoriSerializer,
    AvisSerializer, AvisCreateSerializer, ClientCommandeSerializer,
    CommandeCreateSerializer, 
    DetailsClientSerializer
)
import logging









class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = SignupSerializer(data=request.data, context={'request': request})  # FIX ICI
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({"message": "Utilisateur créé avec succès"}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
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

        # Ne pas utiliser login() ici, faire une session manuelle
        request.session['user_id'] = utilisateur.id_utilisateur  # stocker l'id dans la session

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
        # Vérification session
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({"error": "Vous devez être connecté pour créer une boutique."}, status=401)

        try:
            #  Récupération utilisateur
            utilisateur = Utilisateur.objects.get(id_utilisateur=user_id)
        except Utilisateur.DoesNotExist:
            return Response({"error": "Utilisateur invalide."}, status=401)

        # Vérification type vendeur
        if utilisateur.type_utilisateur != 'vendeur':
            return Response({"error": "Seuls les vendeurs peuvent créer un profil boutique."}, status=403)

        # Vérification profil existant
        if hasattr(utilisateur, 'profil_vendeur'):
            return Response({"error": "Le profil vendeur existe déjà."}, status=400)

        # Validation données
        serializer = ProfilVendeurSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Création profil avec utilisateur
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
        except Utilisateur.DoesNotExist:
            return Response({"error": "Utilisateur non trouvé."}, status=401)

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
            # Seulement les produits avec du stock
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
        
        # Pagination
        page = self.paginate_queryset(queryset.distinct())
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset.distinct(), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def nouveaute(self, request):
        """Récupère les nouveaux produits (derniers 30 jours)"""
        from datetime import timedelta
        date_limite = timezone.now() - timedelta(days=30)
        
        queryset = self.get_queryset().filter(
            # Simuler date_creation avec l'ID (plus récent = ID plus élevé)
            id__gte=self.get_queryset().order_by('-id').first().id - 50
        )[:20]
        
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
        
        # Pagination
        page = self.paginate_queryset(produits)
        if page is not None:
            serializer = ClientProduitSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ClientProduitSerializer(produits, many=True)
        return Response(serializer.data)

# 
# SOLUTION TEMPORAIRE - Dans votre views.py

# Option 1: TEMPORAIRE pour tester - Changer les permissions
from rest_framework.permissions import AllowAny

class PanierViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion du panier"""
    serializer_class = PanierSerializer
    permission_classes = [AllowAny]  # ✅ TEMPORAIRE
    
    def get_queryset(self):
        """Récupérer les articles du panier du premier client disponible"""
        try:
            # ✅ UTILISER LE PREMIER CLIENT DISPONIBLE
            client = DetailsClient.objects.first()
            if not client:
                return Panier.objects.none()
            
            return Panier.objects.filter(client=client).select_related(
                'specification', 'specification__produit'
            ).prefetch_related('specification__produit__imageproduit_set')
        except:
            return Panier.objects.none()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PanierCreateSerializer
        return PanierSerializer
    
    def perform_create(self, serializer):
        """Ajouter un produit au panier"""
        try:
            # ✅ UTILISER LE PREMIER CLIENT DISPONIBLE
            client = DetailsClient.objects.first()
            if not client:
                raise Exception("Aucun client trouvé dans la base de données")
                
            specification = serializer.validated_data['specification']
            quantite = serializer.validated_data['quantite']
            
            # Vérifier si l'article existe déjà
            panier_existant = Panier.objects.filter(
                client=client, 
                specification=specification
            ).first()
            
            if panier_existant:
                # Mettre à jour la quantité existante
                nouvelle_quantite = panier_existant.quantite + quantite
                
                # Vérifier le stock
                if nouvelle_quantite > specification.quantite_stock:
                    raise Exception(
                        f"Stock insuffisant. Disponible: {specification.quantite_stock}, "
                        f"déjà dans panier: {panier_existant.quantite}"
                    )
                
                panier_existant.quantite = nouvelle_quantite
                panier_existant.save()
                return panier_existant
            else:
                # Créer nouvel article
                return serializer.save(client=client)
                
        except Exception as e:
            logger.error(f"Erreur ajout panier: {str(e)}")
            raise Exception(f"Erreur lors de l'ajout au panier: {str(e)}")
    
    def perform_update(self, serializer):
        """Mettre à jour la quantité d'un article"""
        try:
            client = DetailsClient.objects.first()
            if not client:
                raise Exception("Aucun client trouvé")
            if serializer.instance.client != client:
                raise Exception("Vous ne pouvez modifier que vos articles")
            serializer.save()
        except Exception as e:
            logger.error(f"Erreur modification panier: {str(e)}")
            raise Exception(f"Erreur lors de la modification: {str(e)}")
    
    def perform_destroy(self, instance):
        """Supprimer un article du panier"""
        try:
            client = DetailsClient.objects.first()
            if not client:
                raise Exception("Aucun client trouvé")
            if instance.client != client:
                raise Exception("Vous ne pouvez supprimer que vos articles")
            instance.delete()
        except Exception as e:
            logger.error(f"Erreur suppression panier: {str(e)}")
            raise Exception(f"Erreur lors de la suppression: {str(e)}")
    
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

    @action(detail=False, methods=['post'])
    def ajouter_rapide(self, request):
        """Ajouter rapidement un produit avec sa spécification par défaut"""
        try:
            produit_id = request.data.get('produit_id')
            quantite = request.data.get('quantite', 1)
            
            logger.info(f"Tentative ajout produit {produit_id}, quantité {quantite}")
            
            if not produit_id:
                return Response(
                    {'error': 'ID produit requis', 'success': False}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # ✅ VÉRIFIER QU'UN CLIENT EXISTE
            client = DetailsClient.objects.first()
            if not client:
                return Response(
                    {'error': 'Aucun client trouvé dans la base de données', 'success': False}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            logger.info(f"Client trouvé: {client.nom} {client.prenom} (ID: {client.id})")
            
            # Trouver la spécification par défaut du produit
            specification = SpecificationProduit.objects.filter(
                produit_id=produit_id, 
                est_defaut=True
            ).first()
            
            if not specification:
                # Prendre la première spécification disponible
                specification = SpecificationProduit.objects.filter(
                    produit_id=produit_id
                ).first()
            
            if not specification:
                return Response(
                    {'error': f'Aucune spécification trouvée pour le produit {produit_id}', 'success': False}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            logger.info(f"Spécification trouvée: {specification.nom} (ID: {specification.id})")
            
            # ✅ CRÉER DIRECTEMENT L'OBJET PANIER
            panier_existant = Panier.objects.filter(
                client=client, 
                specification=specification
            ).first()
            
            if panier_existant:
                # Mettre à jour la quantité existante
                nouvelle_quantite = panier_existant.quantite + quantite
                
                # Vérifier le stock
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
                # Vérifier le stock
                if quantite > specification.quantite_stock:
                    return Response(
                        {
                            'error': f'Quantité demandée ({quantite}) supérieure au stock disponible ({specification.quantite_stock})', 
                            'success': False
                        }, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Créer nouvel article
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
            logger.error(f"Erreur ajout rapide panier: {str(e)}")
            return Response(
                {'error': f'Erreur lors de l\'ajout: {str(e)}', 'success': False}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        
class FavoriViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des favoris"""
    serializer_class = FavoriSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        try:
            client = self.request.user.detailsclient
            return Favori.objects.filter(client=client).select_related(
                'produit', 'produit__categorie'
            ).prefetch_related('produit__imageproduit_set')
        except:
            return Favori.objects.none()
    
    def perform_create(self, serializer):
        try:
            client = self.request.user.detailsclient
            produit = serializer.validated_data['produit']
            
            # Vérifier si déjà en favori
            if Favori.objects.filter(client=client, produit=produit).exists():
                raise serializers.ValidationError("Produit déjà dans les favoris")
            
            serializer.save(client=client)
        except Exception as e:
            raise serializers.ValidationError(str(e))
    
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """Ajouter/retirer un produit des favoris"""
        produit_id = request.data.get('produit_id')
        if not produit_id:
            return Response(
                {'error': 'produit_id requis'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            client = request.user.detailsclient
            produit = Produit.objects.get(id=produit_id)
            
            favori = Favori.objects.filter(client=client, produit=produit).first()
            if favori:
                favori.delete()
                return Response({'message': 'Retiré des favoris', 'is_favori': False})
            else:
                Favori.objects.create(client=client, produit=produit)
                return Response({'message': 'Ajouté aux favoris', 'is_favori': True})
                
        except Produit.DoesNotExist:
            return Response(
                {'error': 'Produit non trouvé'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
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
            
            # Vérifier si l'utilisateur a déjà donné un avis
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
                
                # Calculer le montant total
                montant_total = sum(
                    (item.specification.prix_promo or item.specification.prix) * item.quantite 
                    for item in panier_items
                )
                
                # Créer la commande
                commande = Commande.objects.create(
                    client=client,
                    montant_total=montant_total,
                    statut='en_attente'
                )
                
                # Créer les détails de commande
                for item in panier_items:
                    DetailCommande.objects.create(
                        commande=commande,
                        specification=item.specification,
                        quantite=item.quantite,
                        prix_unitaire=item.specification.prix_promo or item.specification.prix
                    )
                    
                    # Réduire le stock
                    item.specification.quantite_stock -= item.quantite
                    item.specification.save()
                
                # Vider le panier
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
    

from .models import Commande, DetailCommande, TrackingCommande
from .serializers import CommandeSerializer, DetailCommandeSerializer

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
        """
        ✅ CORRECTION : Récupère l'historique de tracking d'une commande
        URL: /api/commandes/{id}/tracking/
        """
        try:
            commande = self.get_object()
            
            # Récupérer l'historique de tracking
            tracking_entries = TrackingCommande.objects.filter(
                commande=commande
            ).order_by('-date_modification')
            
            # Si aucun historique n'existe, créer une entrée basique
            if not tracking_entries.exists():
                TrackingCommande.objects.create(
                    commande=commande,
                    ancien_statut=None,
                    nouveau_statut=commande.statut
                )
                # Récupérer à nouveau après création
                tracking_entries = TrackingCommande.objects.filter(
                    commande=commande
                ).order_by('-date_modification')
            
            # Sérialiser les données
            tracking_data = []
            for entry in tracking_entries:
                tracking_data.append({
                    'ancien_statut': entry.ancien_statut,
                    'nouveau_statut': entry.nouveau_statut,
                    'date_modification': entry.date_modification.isoformat(),
                })
            
            return Response(tracking_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Log de l'erreur pour debug
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erreur tracking commande {pk}: {str(e)}")
            
            return Response(
                {'error': f'Erreur lors de la récupération du tracking: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
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
