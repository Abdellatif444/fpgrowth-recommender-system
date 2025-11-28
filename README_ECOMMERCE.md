# Guide d'utilisation E-Commerce

Ce projet a été transformé en une application E-Commerce complète avec une interface moderne et des fonctionnalités d'IA.

## 🚀 Démarrage Rapide

1. **Lancer le backend** :
   ```bash
   cd backend
   python app.py
   ```

2. **Accéder à l'application** :
   Ouvrez votre navigateur sur : `http://localhost:5000`

## 👥 Accès

L'application dispose de deux rôles (identifiants de démonstration) :

### 1. Administrateur
- **Login** : `admin`
- **Mot de passe** : `admin123`
- **Fonctionnalités** :
  - Gestion du catalogue produits
  - Ajout d'images, prix et descriptions
  - Visualisation des ventes

### 2. Client
- **Login** : `client`
- **Mot de passe** : `client123`
- **Fonctionnalités** :
  - Navigation dans le catalogue
  - Ajout au panier
  - Recommandations personnalisées en temps réel (FP-Growth)
  - Chatbot assistant shopping (LLM)
  - Passage de commande

## 🔧 Fonctionnalités Techniques

- **Backend** : Flask (Python)
- **Frontend** : HTML5, CSS3 (Glassmorphism), JS
- **Base de données** : PostgreSQL (via Docker) ou Excel (fallback)
- **IA** : 
  - Algorithme FP-Growth pour les associations
  - LLM pour le chatbot et les explications

## 📁 Structure des Fichiers

- `backend/app.py` : Serveur API et fichiers statiques
- `backend/products_manager.py` : Gestion des métadonnées produits (JSON)
- `frontend/` : Fichiers HTML/CSS/JS
  - `index.html` : Page d'accueil
  - `login.html` : Page de connexion
  - `dashboard.html` : Interface client
  - `admin.html` : Interface administrateur
  - `images/products/` : Stockage des images uploadées
