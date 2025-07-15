# debug_produits_zero.py
# Script pour comprendre pourquoi /produits/ retourne 0 produits

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def compare_endpoints():
    """Compare les deux endpoints qui accèdent aux produits"""
    print("🔍 COMPARAISON DES ENDPOINTS PRODUITS")
    print("=" * 45)
    
    # Test endpoint normal
    print("1️⃣ Endpoint normal /produits/")
    try:
        response = requests.get(f"{BASE_URL}/produits/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: 200")
            print(f"   📦 Count: {data.get('count', 'N/A')}")
            print(f"   📋 Results: {len(data.get('results', []))}")
        else:
            print(f"   ❌ Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")
    
    # Test endpoint modération  
    print("\n2️⃣ Endpoint modération /admin/moderation/produits/")
    try:
        response = requests.get(f"{BASE_URL}/admin/moderation/produits/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: 200")
            print(f"   📦 Count: {data.get('count', len(data) if isinstance(data, list) else 'N/A')}")
            if isinstance(data, list):
                print(f"   📋 Results: {len(data)}")
                if data:
                    print(f"   📝 Exemple: {data[0].get('nom', 'N/A')} (ID: {data[0].get('id', 'N/A')})")
            elif 'results' in data:
                print(f"   📋 Results: {len(data['results'])}")
        else:
            print(f"   ❌ Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")

def test_specific_product():
    """Test d'accès à un produit spécifique"""
    print(f"\n🎯 TEST PRODUIT SPÉCIFIQUE")
    print("=" * 30)
    
    # Utiliser un ID que nous savons existant
    product_id = 41  # D'après vos logs: "Chaussures Adidas UltraBoost"
    
    try:
        response = requests.get(f"{BASE_URL}/produits/{product_id}/")
        print(f"📋 Test GET /produits/{product_id}/")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Produit trouvé: {data.get('nom', 'N/A')}")
            print(f"   🏷️ Catégorie: {data.get('categorie', {}).get('nom', 'N/A') if data.get('categorie') else 'Aucune'}")
            print(f"   🏪 Commerçant: {data.get('commercant', 'N/A')}")
            print(f"   💰 Prix min: {data.get('prix_min', 'N/A')}")
            print(f"   📦 Stock: {data.get('stock_total', 'N/A')}")
        elif response.status_code == 404:
            print(f"   ❌ Produit {product_id} non trouvé via /produits/")
        else:
            print(f"   ⚠️ Erreur {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")

def test_filters_and_params():
    """Test avec différents paramètres"""
    print(f"\n🔧 TEST AVEC PARAMÈTRES")
    print("=" * 28)
    
    params_to_test = [
        ("", "Sans paramètres"),
        ("?page=1", "Avec pagination"),
        ("?ordering=nom", "Avec tri par nom"),
        ("?search=", "Recherche vide"),
    ]
    
    for param, description in params_to_test:
        try:
            response = requests.get(f"{BASE_URL}/produits/{param}")
            print(f"📡 {description}: Status {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', len(data) if isinstance(data, list) else 0)
                print(f"   📦 Résultats: {count}")
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")

def check_database_direct():
    """Vérification directe en base (si possible)"""
    print(f"\n💾 SUGGESTIONS VÉRIFICATION BASE")
    print("=" * 38)
    
    print("Pour vérifier directement en base, exécutez :")
    print("python manage.py shell")
    print(">>> from myapp.models import Produit")
    print(">>> print(f'Total produits: {Produit.objects.count()}')")
    print(">>> for p in Produit.objects.all()[:5]:")
    print(">>>     print(f'- {p.nom} (ID: {p.id})')")

def main():
    print("🚀 DIAGNOSTIC - POURQUOI 0 PRODUITS ?")
    print("=" * 50)
    print("Votre API fonctionne, mais /produits/ retourne 0 résultats")
    print("Analysons pourquoi...\n")
    
    compare_endpoints()
    test_specific_product()
    test_filters_and_params()
    check_database_direct()
    
    print(f"\n💡 HYPOTHÈSES PROBABLES:")
    print("1. Les produits sont dans la base mais avec un statut particulier")
    print("2. Le ViewSet ProduitViewSet a des filtres différents de la modération")
    print("3. Les produits sont associés à DetailsCommercant mais le ViewSet cherche ProfilVendeur")
    print("4. Un filtre par défaut cache les produits (ex: stock > 0)")
    
    print(f"\n🎯 PROCHAINES ÉTAPES:")
    print("1. Exécutez les vérifications en base suggérées ci-dessus")
    print("2. Si vous voyez des produits en base, le problème est dans le ViewSet")
    print("3. Si pas de produits en base, ils sont seulement accessibles via modération")

if __name__ == "__main__":
    main()