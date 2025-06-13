# myapp/views.py - VERSION FINALE COMPLÈTE ET CORRIGÉE ✅

# Imports groupés et organisés
import os
import uuid
import logging
import traceback

from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

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
from . import serializers

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