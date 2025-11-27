# 🛒 FP-Growth Recommender System

Système de recommandation de produits utilisant l'algorithme FP-Growth pour l'analyse des associations et la génération de recommandations personnalisées.

## 👥 Auteurs

- **Student A**
- **Student Y**

**Institution:** École Hassania des Travaux Publics (EHTP)  
**Module:** Intelligence Artificielle Multi-Agents  
**Date:** Novembre 2025

---

## 📊 Aperçu

Ce projet implémente un système complet de recommandation basé sur l'algorithme **FP-Growth** (Frequent Pattern Growth) avec :

- 🔍 Analyse des transactions et extraction d'itemsets fréquents
- 📋 Génération de règles d'association (support, confiance, lift)
- 💡 Système de recommandation intelligent
- 🎨 Interface web moderne et responsive
- 🗄️ Persistance des données dans PostgreSQL
- 🐳 Déploiement simplifié avec Docker

---

## 🏗️ Architecture

```
┌─────────────────────┐
│   Frontend          │  HTML/CSS/JS
│   (Nginx)           │  Interface utilisateur
└──────────┬──────────┘
           │ HTTP REST
┌──────────▼──────────┐
│   Backend           │  Flask (Python 3.11)
│   (API REST)        │  Logique métier
└─────┬────────┬──────┘
      │        │
┌─────▼──┐  ┌─▼────────────┐
│FP-Growth│  │ Recommender  │  mlxtend
│ Engine  │  │ Rules Engine │  Règles d'association
└────┬────┘  └──────┬───────┘
     │              │
     │   ┌──────────▼───────┐
     └───►  PostgreSQL 15   │  Persistance
         │  Transactions    │
         └──────────────────┘
```

---

## 🚀 Technologies

- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Backend:** Flask (Python 3.11)
- **Algorithme:** FP-Growth (mlxtend)
- **Base de données:** PostgreSQL 15
- **Containerisation:** Docker & Docker Compose
- **Dataset:** Online Retail Dataset (UCI ML Repository)

---

## 📦 Installation

### Prérequis

- Docker Desktop installé et démarré
- Git (pour cloner le projet)
- Le dataset `Online Retail.xlsx` (à placer dans le dossier `data/`)

### Étapes

1. **Cloner le projet**
   ```bash
   git clone <votre-repo-url>
   cd fpgrowth-recommender-system
   ```

2. **Configurer l'environnement**
   ```bash
   # Copier le fichier d'exemple
   cp .env.example .env
   
   # Éditer .env et modifier les valeurs sensibles
   # Notamment: POSTGRES_PASSWORD et SECRET_KEY
   ```

3. **Télécharger le dataset**
   - Téléchargez `Online Retail.xlsx` depuis [UCI ML Repository](https://archive.ics.uci.edu/ml/datasets/online+retail)
   - Placez-le dans le dossier `data/`

4. **Lancer l'application**
   
   **Windows:**
   ```bash
   .\start.bat
   # Choisir l'option 1: Démarrer/Reconstruire
   ```
   
   **Linux/Mac:**
   ```bash
   docker-compose up --build
   ```

5. **Accéder à l'application**
   - Frontend: http://localhost:8082
   - API: http://localhost:5000/api/health

---

## 📊 Utilisation

### 1. Charger les données
- Cliquez sur **"📥 Charger les Données"**
- Attendez le chargement et nettoyage (30-60s)

### 2. Lancer l'analyse FP-Growth
- Ajustez les paramètres (support, confiance) si nécessaire
- Cliquez sur **"🔍 Lancer l'Analyse FP-Growth"**
- L'analyse prend 3-5 minutes selon les paramètres

### 3. Explorer les résultats
- **Itemsets Fréquents**: Groupes de produits souvent achetés ensemble
- **Règles d'Association**: Relations A → B avec métriques
- **Recommandations**: Testez le système avec des produits

### 4. Supprimer les données
- Cliquez sur **"🗑️ Supprimer"** pour vider la base
- Utile pour recommencer avec de nouveaux paramètres

---

## 📚 API Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/health` | Vérifier l'état de l'API |
| GET | `/api/info` | Informations sur l'application |
| POST | `/api/load-data` | Charger et nettoyer les données |
| GET | `/api/stats` | Statistiques du dataset |
| POST | `/api/analyze` | Lancer l'analyse FP-Growth |
| GET | `/api/itemsets` | Récupérer les itemsets fréquents |
| GET | `/api/rules` | Récupérer les règles d'association |
| POST | `/api/recommend` | Obtenir des recommandations |
| POST | `/api/clear-data` | Supprimer toutes les données |

---

## 🎯 Fonctionnalités

✅ Chargement automatique des données au démarrage  
✅ Persistance PostgreSQL (pas de rechargement à chaque démarrage)  
✅ Nettoyage automatique des données  
✅ Analyse FP-Growth avec paramètres configurables  
✅ Génération de règles d'association  
✅ Système de recommandation intelligent  
✅ Interface moderne avec dark theme  
✅ Responsive design  
✅ Suppression complète des données  

---

## 🔧 Configuration

### Variables d'environnement (`.env`)

```bash
# PostgreSQL
POSTGRES_DB=fpgrowth_db
POSTGRES_USER=fpgrowth_user
POSTGRES_PASSWORD=votre_mot_de_passe_securise

# Flask
SECRET_KEY=votre_cle_secrete_aleatoire
FLASK_ENV=development

# FP-Growth
MIN_SUPPORT=0.01       # Support minimum (0.001 - 1.0)
MIN_CONFIDENCE=0.5     # Confiance minimum (0.1 - 1.0)
```

⚠️ **Sécurité:** Ne jamais commiter le fichier `.env` sur GitHub !

---

## 🐳 Docker Services

- **database**: PostgreSQL 15
- **backend**: Flask API (Python 3.11)
- **frontend**: Nginx (serveur HTTP)

---

## 📂 Structure du Projet

```
fpgrowth-recommender-system/
├── backend/
│   ├── app.py                 # API Flask principale
│   ├── fpgrowth_engine.py     # Moteur FP-Growth
│   ├── recommender.py         # Système de recommandation
│   ├── database.py            # Gestion PostgreSQL
│   ├── data_loader.py         # Chargement des données
│   ├── requirements.txt       # Dépendances Python
│   └── Dockerfile             # Image Docker backend
├── frontend/
│   ├── index.html             # Interface utilisateur
│   ├── css/style.css          # Styles modernes
│   └── js/app.js              # Logique frontend
├── database/
│   └── init.sql               # Script d'initialisation DB
├── data/
│   └── Online Retail.xlsx     # Dataset (non versionné)
├── docker-compose.yml         # Orchestration Docker
├── .env.example               # Exemple de configuration
├── .gitignore                 # Fichiers à ignorer
└── README.md                  # Documentation
```

---

## 🧪 Algorithme FP-Growth

### Principe

FP-Growth est un algorithme efficace pour l'extraction d'itemsets fréquents et la génération de règles d'association.

### Avantages vs Apriori

| Critère | FP-Growth | Apriori |
|---------|-----------|---------|
| Passages sur les données | 2 | k+1 |
| Génération de candidats | Non | Oui |
| Vitesse | ⚡ Rapide | 🐌 Lent |

### Métriques Utilisées

- **Support**: Fréquence d'apparition (% de transactions)
- **Confiance**: Probabilité P(B|A) = Support(A∪B) / Support(A)
- **Lift**: Force de l'association = Confiance(A→B) / Support(B)

---

## 🛠️ Troubleshooting

### Port 8082 déjà utilisé
```bash
# Modifier le port dans docker-compose.yml
# Ligne frontend > ports: "8083:80"
```

### Données pas chargées
```bash
# Vérifier que le dataset existe
ls data/Online\ Retail.xlsx

# Reconstruire les conteneurs
docker-compose down -v
docker-compose up --build
```

### Erreur de connexion PostgreSQL
```bash
# Vérifier les logs
docker-compose logs database

# Réinitialiser le volume
docker-compose down -v
```

---

## 📖 Documentation Complète

Pour plus de détails, consultez :
- `GUIDE_DEMARRAGE.md` - Guide de démarrage complet
- `ETAPES_EXECUTION.md` - Étapes détaillées d'utilisation
- `PRESENTATION.md` - Résumé pour présentation

---

## 📜 Licence

Projet Académique - EHTP 2025

---

## 🙏 Remerciements

- UCI Machine Learning Repository pour le dataset
- mlxtend library pour l'implémentation FP-Growth
- EHTP pour le support académique

---

**Développé avec ❤️ par Student A & Student Y**
