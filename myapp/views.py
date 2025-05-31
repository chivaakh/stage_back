# myapp/views.py - VERSION COMPLÈTE avec tous les ViewSets

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
