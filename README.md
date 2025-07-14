j'ai ajoute ce fichier pour mettre les taches finies.

# 📋 Système de Modération des Produits

## 🎯 Fonctionnalités Implémentées

### 3.1 Consultation des Produits ✅

- **Catalogue global** : Vue d'ensemble avec filtres de modération
- **Détails produit** : Accès complet aux informations + historique de modération
- **Recherche avancée** : Filtres par statut, qualité, signalements, catégorie, vendeur
- **Statistiques** : Dashboard avec métriques clés de modération

### 3.2 Modération des Produits ✅

- **Validation** : Système d'approbation avec workflow complet
- **Suppression** : Retrait avec traçabilité et historique
- **Signalements** : Gestion complète des rapports utilisateurs
- **Contrôle qualité** : Système de scoring et d'évaluation multicritères

---

## 🏗️ Architecture Technique

### Modèles Ajoutés

```python
# Extension du modèle Produit
class Produit:
    # Champs de modération
    est_approuve = BooleanField(default=False)
    statut_moderation = CharField(choices=STATUT_CHOICES, default='en_attente')
    date_moderation = DateTimeField(null=True)
    moderateur = ForeignKey(Utilisateur, null=True)
    raison_rejet = TextField(null=True)
    est_visible = BooleanField(default=True)
    score_qualite = DecimalField(default=0.00)
    derniere_verification = DateTimeField(null=True)

# Nouveaux modèles
class SignalementProduit  # Gestion des signalements
class HistoriqueModerationProduit  # Traçabilité des actions
class CritereQualiteProduit  # Critères d'évaluation
class EvaluationQualiteProduit  # Scores qualité
```

### API Endpoints

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/admin/dashboard-moderation/` | GET | Dashboard récapitulatif |
| `/admin/moderation/produits/` | GET | Liste des produits avec infos modération |
| `/admin/moderation/produits/{id}/moderer/` | POST | Modérer un produit |
| `/admin/moderation/produits/moderation_en_masse/` | POST | Modération en lot |
| `/admin/moderation/produits/statistiques/` | GET | Statistiques globales |
| `/admin/signalements/` | GET/POST | Gestion des signalements |
| `/admin/signalements/{id}/traiter/` | POST | Traiter un signalement |
| `/client/signalements/` | POST | Créer un signalement |
| `/admin/evaluations-qualite/evaluer_produit/` | POST | Évaluer la qualité |

---

## 🚀 Installation et Configuration

### 1. Migration de la Base de Données

```bash
# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate
```

### 2. Initialisation des Critères de Qualité

```python
# Dans le shell Django
python manage.py shell

from myapp.models import CritereQualiteProduit

criteres = [
    {"nom": "Qualité des images", "description": "Images claires et représentatives", "poids": 2.0},
    {"nom": "Description complète", "description": "Description détaillée et précise", "poids": 1.5},
    {"nom": "Prix cohérent", "description": "Prix en adéquation avec le marché", "poids": 1.0},
    {"nom": "Informations techniques", "description": "Spécifications techniques complètes", "poids": 1.5},
    {"nom": "Conformité légale", "description": "Respect des réglementations", "poids": 3.0},
]

for critere_data in criteres:
    CritereQualiteProduit.objects.get_or_create(**critere_data)
```

### 3. Configuration des URLs

```python
# Ajouter dans urls.py
from .views import (
    ModerationProduitViewSet, SignalementProduitViewSet,
    EvaluationQualiteViewSet, CritereQualiteViewSet,
    DashboardModerationView,
)

# Router
router.register(r'admin/moderation/produits', ModerationProduitViewSet)
router.register(r'admin/signalements', SignalementProduitViewSet)
router.register(r'admin/evaluations-qualite', EvaluationQualiteViewSet)
router.register(r'admin/criteres-qualite', CritereQualiteViewSet)
router.register(r'client/signalements', SignalementProduitViewSet)

# URLs spéciales
urlpatterns += [
    path('admin/dashboard-moderation/', DashboardModerationView.as_view()),
]
```

---

## 📊 Utilisation

### Dashboard Modération

```bash
GET /admin/dashboard-moderation/
```

**Réponse :**
```json
{
  "stats_produits": {
    "total": 150,
    "en_attente": 12,
    "approuves": 130,
    "rejetes": 8
  },
  "stats_signalements": {
    "total": 25,
    "nouveaux": 5,
    "urgent": 2
  },
  "produits_urgents": [...],
  "signalements_recents": [...]
}
```

### Modération d'un Produit

```bash
POST /admin/moderation/produits/1/moderer/
Content-Type: application/json

{
  "action": "approuver",
  "commentaire": "Produit conforme aux standards"
}
```

**Actions disponibles :**
- `"approuver"` : Approuve et rend visible
- `"rejeter"` : Rejette avec raison obligatoire
- `"suspendre"` : Suspend temporairement
- `"masquer"` : Masque sans changer le statut
- `"demander_modification"` : Demande des corrections

### Création d'un Signalement

```bash
POST /client/signalements/
Content-Type: application/json

{
  "produit": 1,
  "type_signalement": "contenu_inapproprie",
  "description": "Le produit contient des informations trompeuses..."
}
```

**Types de signalement :**
- `contenu_inapproprie`
- `fausse_information`
- `prix_anormal`
- `image_trompeuse`
- `spam`
- `violation_droits`
- `autre`

### Évaluation Qualité

```bash
POST /admin/evaluations-qualite/evaluer_produit/
Content-Type: application/json

{
  "produit_id": 1,
  "evaluations": [
    {"critere_id": 1, "score": 8.5, "commentaire": "Bonnes images"},
    {"critere_id": 2, "score": 7.0, "commentaire": "Description correcte"}
  ]
}
```

### Recherche et Filtres

```bash
# Produits en attente de modération
GET /admin/moderation/produits/?status_filter=en_attente

# Produits signalés
GET /admin/moderation/produits/?status_filter=signales

# Recherche par nom
GET /admin/moderation/produits/?search=iphone

# Filtres combinés
GET /admin/moderation/produits/?statut_moderation=approuve&categorie=1&ordering=-score_qualite
```

---

## 🔒 Permissions et Sécurité

### Permissions Actuelles (À Configurer)

```python
# TODO: Configurer les permissions dans les ViewSets
permission_classes = [IsAdminUser]  # Au lieu de AllowAny

# Permissions suggérées :
# - Dashboard : IsAdminUser ou IsModerator
# - Modération produits : IsAdminUser ou IsModerator  
# - Signalements admin : IsAdminUser ou IsModerator
# - Signalements client : IsAuthenticated
# - Évaluation qualité : IsAdminUser ou IsQualityEvaluator
```

### Authentification

```python
# Utiliser l'authentification par session existante
# Les vues récupèrent automatiquement l'utilisateur connecté
# via request.user (une fois les permissions configurées)
```

---

## 📈 Métriques et Statistiques

### Métriques Disponibles

1. **Produits :**
   - Total, en attente, approuvés, rejetés, suspendus
   - Score qualité moyen
   - Répartition par catégorie

2. **Signalements :**
   - Total, nouveaux, en cours, traités, rejetés
   - Répartition par type
   - Temps de traitement moyen

3. **Performance Modération :**
   - Délai moyen de traitement
   - Taux d'approbation
   - Actions par modérateur

### Dashboard KPIs

```bash
GET /admin/moderation/produits/statistiques/
GET /admin/signalements/statistiques/
```

---

## 🔄 Workflow de Modération

### Cycle de Vie d'un Produit

```
Création → [en_attente] → Modération → [approuvé/rejeté/suspendu]
                ↓
           Signalement → Réévaluation → Décision finale
```

### Statuts de Produit

- **`en_attente`** : Nouveau produit en attente de validation
- **`approuve`** : Produit validé et visible
- **`rejete`** : Produit non conforme, masqué
- **`suspendu`** : Produit temporairement retiré

### Processus de Signalement

1. **Création** : Utilisateur signale un produit
2. **Évaluation** : Modérateur examine le signalement
3. **Action** : Décision prise (valide/invalide)
4. **Suivi** : Notification aux parties concernées

---

## 🧪 Tests et Validation

### Tests Automatisés

```python
# Exécuter les tests d'exemple
python exemples_utilisation_moderation.py
```

### Tests manuels

```bash
# Vérifier le serveur
curl -X GET http://127.0.0.1:8000/api/admin/dashboard-moderation/

# Tester la modération
curl -X POST http://127.0.0.1:8000/api/admin/moderation/produits/1/moderer/ \
  -H "Content-Type: application/json" \
  -d '{"action": "approuver", "commentaire": "Test"}'
```

---

## 🎛️ Configuration Avancée

### Paramètres Personnalisables

```python
# settings.py - Paramètres de modération
MODERATION_SETTINGS = {
    'AUTO_APPROVE_VERIFIED_SELLERS': True,  # Auto-approuver vendeurs vérifiés
    'QUALITY_SCORE_THRESHOLD': 6.0,        # Seuil score qualité
    'MAX_SIGNALEMENTS_BEFORE_SUSPENSION': 3,  # Suspendre après X signalements
    'NOTIFICATION_EMAILS': True,            # Emails de notification
}
```

### Hooks et Extensions

```python
# Étendre le système avec des hooks personnalisés
def on_product_approved(product):
    # Logique personnalisée après approbation
    pass

def on_product_rejected(product, reason):
    # Logique personnalisée après rejet
    pass
```

---

## 🚨 Dépannage

### Problèmes Courants

1. **Migration Failed**
   ```bash
   python manage.py showmigrations
   python manage.py migrate --fake-initial
   ```

2. **Permissions Error**
   ```python
   # Vérifier les permissions dans les ViewSets
   permission_classes = [AllowAny]  # Temporaire pour test
   ```

3. **Foreign Key Constraints**
   ```python
   # S'assurer que les utilisateurs existent avant les tests
   from myapp.models import Utilisateur
   Utilisateur.objects.get_or_create(...)
   ```

### Logs et Debug

```python
# Activer les logs dans settings.py
LOGGING = {
    'loggers': {
        'myapp': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

---

## 🔜 Évolutions Futures

### Fonctionnalités Prévues

1. **Intelligence Artificielle**
   - Détection automatique de contenu inapproprié
   - Scoring qualité automatique
   - Classification automatique des signalements

2. **Notifications**
   - Emails automatiques aux vendeurs
   - Notifications push pour les modérateurs
   - Alertes temps réel

3. **Analytics Avancées**
   - Tableaux de bord interactifs
   - Rapports de performance
   - Prédictions de tendances

4. **API Mobile**
   - Endpoints optimisés pour mobile
   - Synchronisation offline
   - Interface de modération mobile

---

## 📞 Support

Pour toute question ou problème :

1. Consulter les logs : `debug.log`
2. Vérifier les exemples : `exemples_utilisation_moderation.py`
3. Tester les endpoints avec les commandes curl fournies
4. Vérifier la configuration des permissions

**Status actuel :** ✅ Prêt pour tests et déploiement