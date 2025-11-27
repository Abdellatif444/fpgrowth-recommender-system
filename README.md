# 🛒 Système de Recommandation avec FP-Growth

## 📝 Description
Application web complète de recommandation de produits utilisant l'algorithme FP-Growth pour l'analyse des associations et la génération de recommandations personnalisées.

## 🏗️ Architecture

```
┌─────────────────────┐
│   Frontend          │
│   HTML/CSS/JS       │
└──────────┬──────────┘
           │ HTTP
┌──────────▼──────────┐
│   API REST          │
│   Flask/Python      │
└─────┬────────┬──────┘
      │        │
┌─────▼──┐  ┌─▼────────────┐
│FP-Growth│  │ Recommender  │
│ mlxtend │  │Rules Engine  │
└────┬────┘  └──────┬───────┘
     │              │
     │   ┌──────────▼───────┐
     └───►  PostgreSQL      │
         │  Transactions    │
         └──────────────────┘
```

## 🚀 Technologies Utilisées

- **Frontend** : HTML5, CSS3, JavaScript (Vanilla)
- **Backend** : Flask (Python 3.11)
- **Algorithme** : FP-Growth (mlxtend)
- **Base de données** : PostgreSQL 15
- **Containerisation** : Docker & Docker Compose
- **Dataset** : Online Retail Dataset

## 📦 Structure du Projet

```
fpgrowth-recommender-system/
├── backend/
│   ├── app.py                 # API Flask
│   ├── fpgrowth_engine.py     # Moteur FP-Growth
│   ├── recommender.py         # Système de recommandation
│   ├── database.py            # Connexion PostgreSQL
│   ├── data_loader.py         # Chargement du dataset
│   ├── requirements.txt       # Dépendances Python
│   └── Dockerfile            # Image Docker Backend
├── frontend/
│   ├── index.html            # Interface utilisateur
│   ├── css/
│   │   └── style.css         # Styles
│   └── js/
│       └── app.js            # Logique frontend
├── database/
│   ├── init.sql              # Initialisation DB
│   └── Dockerfile            # Image PostgreSQL
├── data/
│   └── Online Retail.xlsx    # Dataset
├── docker-compose.yml        # Orchestration
├── .env                      # Variables d'environnement
└── README.md                 # Documentation
```

## 🎯 Fonctionnalités

1. **Analyse FP-Growth** : Extraction des itemsets fréquents et règles d'association
2. **Recommandations** : Suggestions de produits basées sur le panier actuel
3. **Visualisation** : Dashboard interactif des résultats
4. **API REST** : Endpoints pour l'intégration
5. **Persistance** : Stockage des transactions et résultats

## 🔧 Installation et Démarrage

### Prérequis
- Docker Desktop installé
- Git (optionnel)

### Étapes

1. **Copier le dataset**
```bash
# Le dataset est déjà dans ../dataset/Online Retail.xlsx
```

2. **Lancer l'application**
```bash
cd fpgrowth-recommender-system
docker-compose up --build
```

3. **Accéder à l'application**
- Frontend : http://localhost:8082
- API : http://localhost:5000
- Database : localhost:5432

## 📊 Endpoints API

### GET /api/health
Vérification de l'état de l'API

### POST /api/analyze
Analyse FP-Growth sur les transactions
```json
{
  "min_support": 0.01,
  "min_confidence": 0.5
}
```

### POST /api/recommend
Obtenir des recommandations
```json
{
  "items": ["PRODUCT_A", "PRODUCT_B"]
}
```

### GET /api/stats
Statistiques globales du dataset

## 👥 Auteurs

- **Student A**
- **Student Y**

## 🏫 Institution

École Hassania des Travaux Publics (EHTP)  
Génie Informatique - Intelligence Artificielle Multi-Agents

## 📅 Date

Novembre 2025
