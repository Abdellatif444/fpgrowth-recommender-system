# 🚀 Guide de Démarrage Rapide

## Prérequis

- Docker Desktop installé et en cours d'exécution
- Au moins 4 GB de RAM disponible
- Ports 5000, 5432 et 8080 disponibles

## Étapes de Démarrage

### 1. Vérifier que Docker est en cours d'exécution

```powershell
docker --version
docker-compose --version
```

### 2. Se placer dans le dossier du projet

```powershell
cd fpgrowth-recommender-system
```

### 3. Lancer l'application avec Docker Compose

```powershell
docker-compose up --build
```

Cette commande va :
- ✅ Construire les images Docker pour le backend
- ✅ Démarrer PostgreSQL
- ✅ Démarrer l'API Flask
- ✅ Démarrer le serveur web Nginx pour le frontend

### 4. Attendre que tous les services soient prêts

Vous devriez voir dans les logs :
```
fpgrowth_db       | database system is ready to accept connections
fpgrowth_backend  | Running on http://0.0.0.0:5000
fpgrowth_frontend | start worker processes
```

### 5. Accéder à l'application

Ouvrez votre navigateur et allez sur :
- **Frontend** : http://localhost:8082
- **API** : http://localhost:5000/api/health

## Utilisation de l'Application

### Étape 1 : Charger les Données
1. Cliquez sur le bouton **"Charger les Données"**
2. Attendez que le chargement et le nettoyage soient terminés
3. Les statistiques s'afficheront automatiquement

### Étape 2 : Configurer les Paramètres
1. Ajustez le **Support Minimum** (recommandé : 0.01 = 1%)
2. Ajustez la **Confiance Minimum** (recommandé : 0.5 = 50%)

### Étape 3 : Lancer l'Analyse
1. Cliquez sur **"Lancer l'Analyse FP-Growth"**
2. Attendez que l'analyse soit terminée (peut prendre 1-2 minutes)
3. Les résultats s'afficheront dans les onglets

### Étape 4 : Explorer les Résultats

#### Onglet "Itemsets Fréquents"
- Voir les ensembles de produits fréquemment achetés ensemble
- Trier par support (fréquence d'apparition)

#### Onglet "Règles d'Association"
- Voir les règles du type "Si A alors B"
- Métriques : Support, Confiance, Lift

#### Onglet "Recommandations"
- Entrer des produits dans le panier
- Obtenir des recommandations personnalisées
- Voir la confiance et le lift de chaque recommandation

## Commandes Utiles

### Arrêter l'application
```powershell
# Dans le terminal où docker-compose tourne
Ctrl + C

# Ou dans un autre terminal
docker-compose down
```

### Arrêter et supprimer les volumes (réinitialisation complète)
```powershell
docker-compose down -v
```

### Voir les logs d'un service spécifique
```powershell
docker-compose logs backend
docker-compose logs database
docker-compose logs frontend
```

### Redémarrer un service
```powershell
docker-compose restart backend
```

### Accéder au shell d'un conteneur
```powershell
# Backend Python
docker-compose exec backend sh

# Base de données PostgreSQL
docker-compose exec database psql -U fpgrowth_user -d fpgrowth_db
```

## Résolution de Problèmes

### Problème : Port déjà utilisé
**Solution** : Modifier les ports dans `docker-compose.yml`

### Problème : Erreur de connexion à la base de données
**Solution** : Attendre quelques secondes que PostgreSQL soit complètement démarré

### Problème : L'API ne répond pas
**Solution** : Vérifier les logs avec `docker-compose logs backend`

### Problème : Le frontend ne charge pas
**Solution** : 
1. Vérifier que Nginx est démarré : `docker-compose ps`
2. Vérifier les logs : `docker-compose logs frontend`

## Architecture des Services

```
┌─────────────────────────────────────────┐
│  Frontend (Nginx)                       │
│  Port: 8080                             │
│  http://localhost:8080                  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Backend (Flask API)                    │
│  Port: 5000                             │
│  http://localhost:5000/api              │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Database (PostgreSQL)                  │
│  Port: 5432                             │
│  User: fpgrowth_user                    │
│  DB: fpgrowth_db                        │
└─────────────────────────────────────────┘
```

## Endpoints API Disponibles

### Santé et Information
- `GET /api/health` - Vérifier l'état de l'API
- `GET /api/info` - Informations sur l'application

### Gestion des Données
- `POST /api/load-data` - Charger les données
- `GET /api/stats` - Statistiques des données
- `GET /api/top-products` - Produits les plus vendus

### Analyse FP-Growth
- `POST /api/analyze` - Lancer l'analyse
- `GET /api/itemsets` - Obtenir les itemsets fréquents
- `GET /api/rules` - Obtenir les règles d'association

### Recommandations
- `POST /api/recommend` - Obtenir des recommandations
- `POST /api/frequently-bought-together` - Produits achetés ensemble

## Paramètres Recommandés

### Pour un dataset volumineux (>100k transactions)
```json
{
  "min_support": 0.005,
  "min_confidence": 0.3
}
```

### Pour une analyse rapide
```json
{
  "min_support": 0.02,
  "min_confidence": 0.6
}
```

### Pour une analyse détaillée
```json
{
  "min_support": 0.001,
  "min_confidence": 0.2
}
```

## Support

Pour toute question ou problème :
- Vérifier les logs : `docker-compose logs`
- Consulter la documentation : `README.md`
- Contacter les auteurs : Student A, Student Y

---

**Bon usage ! 🚀**
