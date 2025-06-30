# myapp/views.py - VERSION COMPLÈTE avec tous les ViewSets

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import Produit, ImageProduit, SpecificationProduit
from .serializers import ProduitSerializer, ImageProduitSerializer, SpecificationProduitSerializer
import logging
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import uuid

logger = logging.getLogger(__name__)
from rest_framework import viewsets
# from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from .models import Produit
from .serializers import ProduitSerializer
from . import serializers


# myapp/views.py - Views spécifiques aux clients

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
    ClientProduitSerializer, ClientCategorieSerializer,
    PanierSerializer, PanierCreateSerializer, FavoriSerializer,
    AvisSerializer, AvisCreateSerializer, ClientCommandeSerializer,
    CommandeCreateSerializer, DetailsClientSerializer
)
import logging

logger = logging.getLogger(__name__)

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

class PanierViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion du panier"""
    serializer_class = PanierSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Récupérer seulement les articles du panier du client connecté
        try:
            client = self.request.user.detailsclient
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
        try:
            client = self.request.user.detailsclient
            specification = serializer.validated_data['specification']
            quantite = serializer.validated_data['quantite']
            
            # Vérifier si l'article existe déjà dans le panier
            panier_existant = Panier.objects.filter(
                client=client, 
                specification=specification
            ).first()
            
            if panier_existant:
                # Mettre à jour la quantité
                panier_existant.quantite += quantite
                panier_existant.save()
                return panier_existant
            else:
                # Créer nouvel article
                return serializer.save(client=client)
                
        except Exception as e:
            logger.error(f"Erreur ajout panier: {str(e)}")
            raise serializer.ValidationError("Erreur lors de l'ajout au panier")
    
    @action(detail=False, methods=['get'])
    def resume(self, request):
        """Récupère le résumé du panier"""
        try:
            client = request.user.detailsclient
            panier_items = self.get_queryset()
            
            total_items = sum(item.quantite for item in panier_items)
            total_prix = sum(
                (item.specification.prix_promo or item.specification.prix) * item.quantite 
                for item in panier_items
            )
            
            return Response({
                'total_items': total_items,
                'total_prix': float(total_prix),
                'nombre_articles': panier_items.count()
            })
        except:
            return Response({
                'total_items': 0,
                'total_prix': 0.0,
                'nombre_articles': 0
            })
    
    @action(detail=False, methods=['post'])
    def vider(self, request):
        """Vide complètement le panier"""
        try:
            client = request.user.detailsclient
            count = Panier.objects.filter(client=client).count()
            Panier.objects.filter(client=client).delete()
            return Response({
                'message': f'{count} articles supprimés du panier'
            })
        except:
            return Response(
                {'error': 'Erreur lors du vidage du panier'}, 
                status=status.HTTP_400_BAD_REQUEST
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
    permission_classes = []

    def get_queryset(self):
        """Optimiser les requêtes avec prefetch"""
        return Produit.objects.prefetch_related(
            'imageproduit_set', 'specificationproduit_set'
        ).select_related('commercant', 'categorie')

    def create(self, request, *args, **kwargs):
        """Créer un produit avec images et spécifications"""
        logger.info(f"🔍 Données reçues pour création: {request.data}")
        
        try:
            with transaction.atomic():
                # 1. Extraire les données
                produit_data = {
                    'nom': request.data.get('nom'),
                    'description': request.data.get('description'),
                    'reference': request.data.get('reference'),
                }
                
                images_data = request.data.get('images', [])
                specifications_data = request.data.get('specifications', [])
                
                logger.info(f"📦 Produit: {produit_data}")
                logger.info(f"🖼️ Images: {len(images_data)} images")
                logger.info(f"📋 Spécifications: {len(specifications_data)} specs")
                
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
                                logger.info(f"✅ Image {i+1} créée: {image_obj.url_image}")
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
                    return Response(
                        ProduitSerializer(produit_complet).data, 
                        status=status.HTTP_201_CREATED
                    )
                else:
                    logger.error(f"❌ Erreurs validation produit: {produit_serializer.errors}")
                    return Response(produit_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    
        except Exception as e:
            logger.error(f"❌ Erreur lors de la création complète: {str(e)}")
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
        serializer.save(commercant=commercant)
        
        
        
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated  # ou [] si pas d'auth requis
from .models import SpecificationProduit, MouvementStock
from .serializers import SpecificationProduitSerializer, MouvementStockSerializer

class SpecificationProduitViewSet(viewsets.ModelViewSet):
    queryset = SpecificationProduit.objects.all()
    serializer_class = SpecificationProduitSerializer
    permission_classes = [AllowAny]  # adapte selon besoin

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


@csrf_exempt
@api_view(['POST'])
def upload_image(request):
    """
    Upload une image et retourne son URL
    """
    try:
        if 'image' not in request.FILES:
            return Response(
                {'error': 'Aucune image fournie'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        image_file = request.FILES['image']
        
        # Validation du fichier
        if not image_file.content_type.startswith('image/'):
            return Response(
                {'error': 'Le fichier doit être une image'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Taille max 5MB
        if image_file.size > 5 * 1024 * 1024:
            return Response(
                {'error': 'Fichier trop volumineux (max 5MB)'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Générer un nom unique pour éviter les conflits
        extension = image_file.name.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{extension}"
        
        # Créer le dossier uploads s'il n'existe pas
        upload_path = os.path.join('uploads', 'images')
        os.makedirs(os.path.join(settings.MEDIA_ROOT, upload_path), exist_ok=True)
        
        # Sauvegarder le fichier
        file_path = os.path.join(upload_path, unique_filename)
        saved_path = default_storage.save(file_path, image_file)
        
        # Construire l'URL complète
        image_url = request.build_absolute_uri(settings.MEDIA_URL + saved_path)
        
        return Response({
            'success': True,
            'url': image_url,
            'filename': unique_filename,
            'size': image_file.size
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Erreur serveur: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
# ✅ AJOUT des ViewSets manquants
class ImageProduitViewSet(viewsets.ModelViewSet):
    queryset = ImageProduit.objects.all()
    serializer_class = ImageProduitSerializer
    permission_classes = []

    def get_queryset(self):
        return ImageProduit.objects.select_related('produit').order_by('produit', 'ordre')


class SpecificationProduitViewSet(viewsets.ModelViewSet):
    queryset = SpecificationProduit.objects.all()
    serializer_class = SpecificationProduitSerializer
    permission_classes = []

    def get_queryset(self):
        return SpecificationProduit.objects.select_related('produit').order_by('produit', '-est_defaut')

from rest_framework import viewsets
from .models import Categorie
from .serializers import CategorieSerializer
from rest_framework.permissions import AllowAny

class CategorieViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes = [AllowAny]  # ou adapte selon tes besoins

from rest_framework import viewsets
from rest_framework.permissions import AllowAny  # adapte selon ton besoin
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().order_by('-date_notification')
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]  # adapte pour sécuriser si besoin

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


