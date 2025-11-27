# 📋 Étapes d'Exécution du Projet FP-Growth

## Vue d'Ensemble

Ce document décrit les étapes complètes pour exécuter le projet de recommandation basé sur l'algorithme FP-Growth, depuis le démarrage jusqu'à l'obtention des résultats.

---

## 🎯 Objectif

Créer un système de recommandation de produits utilisant l'algorithme FP-Growth pour analyser les transactions du dataset "Online Retail" et générer des recommandations personnalisées.

---

## 📦 Contenu du Projet

### Structure des Fichiers

```
fpgrowth-recommender-system/
├── backend/                    # API Flask et logique métier
│   ├── app.py                 # Application Flask principale
│   ├── fpgrowth_engine.py     # Moteur FP-Growth (mlxtend)
│   ├── recommender.py         # Système de recommandation
│   ├── database.py            # Gestion PostgreSQL
│   ├── data_loader.py         # Chargement et nettoyage des données
│   ├── requirements.txt       # Dépendances Python
│   └── Dockerfile            # Image Docker backend
│
├── frontend/                   # Interface utilisateur
│   ├── index.html            # Page principale
│   ├── css/style.css         # Styles modernes
│   └── js/app.js             # Logique frontend
│
├── database/                   # Configuration base de données
│   └── init.sql              # Script d'initialisation
│
├── data/                       # Dataset
│   └── Online Retail.xlsx    # Données de transactions
│
├── docker-compose.yml         # Orchestration des services
├── .env                       # Variables d'environnement
└── GUIDE_DEMARRAGE.md        # Guide détaillé
```

---

## 🚀 Étapes d'Exécution

### Étape 1 : Préparation de l'Environnement

#### 1.1 Vérifier Docker
```powershell
# Vérifier que Docker Desktop est installé et en cours d'exécution
docker --version
docker-compose --version
```

**Résultat attendu :**
```
Docker version 24.x.x
Docker Compose version v2.x.x
```

#### 1.2 Naviguer vers le projet
```powershell
cd "c:\Users\Admin\Desktop\ProjectPath\semestre5\Intelligence-Artificielle_Multi-Agents\presentation finale\fpgrowth-recommender-system"
```

---

### Étape 2 : Démarrage de l'Application

#### 2.1 Méthode 1 : Utiliser le script batch (Recommandé)
```powershell
.\start.bat
```
Puis choisir l'option **1** pour démarrer.

#### 2.2 Méthode 2 : Commande Docker Compose directe
```powershell
docker-compose up --build
```

#### 2.3 Attendre le démarrage complet

**Logs à surveiller :**

✅ **PostgreSQL prêt :**
```
fpgrowth_db | database system is ready to accept connections
```

✅ **Backend Flask prêt :**
```
fpgrowth_backend | Running on http://0.0.0.0:5000
fpgrowth_backend | 🚀 Démarrage de l'API FP-Growth Recommender System
```

✅ **Frontend Nginx prêt :**
```
fpgrowth_frontend | start worker processes
```

**Temps de démarrage estimé :** 30-60 secondes

---

### Étape 3 : Accès à l'Application

#### 3.1 Ouvrir le navigateur
Aller sur : **http://localhost:8082**

#### 3.2 Vérifier la connexion API
Le badge de statut en haut à droite doit afficher : **"API connectée"** avec un point vert

---

### Étape 4 : Chargement des Données

#### 4.1 Cliquer sur "Charger les Données"
- Bouton bleu avec icône 📥
- Situé dans le panneau de contrôle

#### 4.2 Attendre le traitement
**Opérations effectuées :**
1. Lecture du fichier Excel (541,909 lignes)
2. Nettoyage des données :
   - Suppression des transactions annulées
   - Suppression des valeurs manquantes
   - Suppression des quantités/prix négatifs
3. Insertion dans PostgreSQL

**Temps estimé :** 20-40 secondes

#### 4.3 Vérifier les statistiques
Les cartes statistiques doivent afficher :
- **Nombre de transactions** : ~400,000
- **Nombre de produits** : ~3,600
- **Nombre de clients** : ~4,300

---

### Étape 5 : Configuration des Paramètres

#### 5.1 Support Minimum
**Définition :** Fréquence minimale d'apparition d'un itemset

**Valeurs recommandées :**
- **Analyse rapide :** 0.02 (2%)
- **Analyse standard :** 0.01 (1%)
- **Analyse détaillée :** 0.005 (0.5%)

**Impact :**
- ⬆️ Valeur élevée → Moins d'itemsets, analyse rapide
- ⬇️ Valeur faible → Plus d'itemsets, analyse lente

#### 5.2 Confiance Minimum
**Définition :** Fiabilité minimale des règles d'association

**Valeurs recommandées :**
- **Règles très fiables :** 0.7 (70%)
- **Règles fiables :** 0.5 (50%)
- **Exploration :** 0.3 (30%)

**Impact :**
- ⬆️ Valeur élevée → Moins de règles, plus fiables
- ⬇️ Valeur faible → Plus de règles, moins fiables

---

### Étape 6 : Lancement de l'Analyse FP-Growth

#### 6.1 Cliquer sur "Lancer l'Analyse FP-Growth"
- Bouton vert avec icône 🔍

#### 6.2 Processus d'analyse
**Opérations effectuées :**
1. Préparation des données (one-hot encoding)
2. Extraction des itemsets fréquents (FP-Growth)
3. Génération des règles d'association
4. Calcul des métriques (support, confiance, lift)
5. Sauvegarde dans PostgreSQL

**Temps estimé :**
- Support 0.02 : ~10-20 secondes
- Support 0.01 : ~30-60 secondes
- Support 0.005 : ~1-2 minutes

#### 6.3 Vérifier les résultats
Les statistiques d'analyse doivent apparaître :
- **Itemsets fréquents** : 100-1000+
- **Règles d'association** : 50-500+
- **Confiance moyenne** : 40-70%
- **Lift moyen** : 2-5

---

### Étape 7 : Exploration des Résultats

#### 7.1 Onglet "Itemsets Fréquents"

**Que voir :**
- Ensembles de produits achetés ensemble
- Support de chaque itemset
- Longueur des itemsets (2, 3, 4+ produits)

**Exemple :**
```
#1 WHITE HANGING HEART T-LIGHT HOLDER + REGENCY CAKESTAND 3 TIER
Support: 2.5%
Longueur: 2
```

**Interprétation :**
Ces deux produits apparaissent ensemble dans 2.5% des transactions.

#### 7.2 Onglet "Règles d'Association"

**Que voir :**
- Règles du type "Si A alors B"
- Métriques : Support, Confiance, Lift

**Exemple :**
```
#1 WHITE HANGING HEART T-LIGHT HOLDER → REGENCY CAKESTAND 3 TIER
Support: 2.5%
Confiance: 65%
Lift: 3.2
```

**Interprétation :**
- **Support 2.5%** : Ces produits apparaissent ensemble dans 2.5% des transactions
- **Confiance 65%** : Quand on achète A, on achète B dans 65% des cas
- **Lift 3.2** : Cette association est 3.2× plus forte que le hasard

**Critères de qualité :**
- ✅ **Lift > 1** : Association positive
- ✅ **Confiance > 50%** : Règle fiable
- ⚠️ **Lift < 1** : Association négative (à éviter)

#### 7.3 Onglet "Recommandations"

**Utilisation :**
1. Entrer des produits dans le champ texte (séparés par des virgules)
2. Cliquer sur "Obtenir des Recommandations"
3. Voir les produits recommandés avec leurs scores

**Exemple d'entrée :**
```
WHITE HANGING HEART T-LIGHT HOLDER, REGENCY CAKESTAND 3 TIER
```

**Résultat attendu :**
```
#1 JUMBO BAG RED RETROSPOT
Confiance: 72%
Lift: 4.1
Basé sur: WHITE HANGING HEART T-LIGHT HOLDER

#2 PARTY BUNTING
Confiance: 68%
Lift: 3.8
Basé sur: REGENCY CAKESTAND 3 TIER
```

---

### Étape 8 : Interprétation des Résultats

#### 8.1 Métriques Clés

**Support**
- Fréquence d'apparition
- Plus élevé = Plus fréquent
- Utilisé pour filtrer les itemsets rares

**Confiance**
- Probabilité conditionnelle
- Confiance(A → B) = P(B|A)
- Mesure la fiabilité de la règle

**Lift**
- Force de l'association
- Lift = Confiance / Support(B)
- Lift > 1 : Association positive
- Lift = 1 : Indépendance
- Lift < 1 : Association négative

**Leverage**
- Différence entre fréquence observée et attendue
- Mesure l'intérêt de la règle

**Conviction**
- Mesure la dépendance
- Conviction élevée = Forte dépendance

#### 8.2 Cas d'Usage Pratiques

**1. Cross-Selling**
Utiliser les règles pour suggérer des produits complémentaires lors de l'achat.

**2. Merchandising**
Placer les produits fréquemment achetés ensemble à proximité en magasin.

**3. Promotions**
Créer des bundles basés sur les itemsets fréquents.

**4. Gestion de Stock**
Anticiper les achats groupés pour optimiser le stock.

---

### Étape 9 : Tests et Validation

#### 9.1 Tester différents paramètres

**Test 1 : Analyse rapide**
```
Support: 0.02
Confiance: 0.6
```
Résultat : Peu de règles, très fiables

**Test 2 : Analyse standard**
```
Support: 0.01
Confiance: 0.5
```
Résultat : Équilibre entre quantité et qualité

**Test 3 : Analyse exploratoire**
```
Support: 0.005
Confiance: 0.3
```
Résultat : Beaucoup de règles, moins fiables

#### 9.2 Vérifier la cohérence

**Questions à se poser :**
- ✅ Les associations ont-elles du sens ?
- ✅ Les produits recommandés sont-ils pertinents ?
- ✅ Les métriques sont-elles dans des plages raisonnables ?

---

### Étape 10 : Arrêt de l'Application

#### 10.1 Méthode 1 : Ctrl+C
Dans le terminal où Docker Compose tourne :
```
Ctrl + C
```

#### 10.2 Méthode 2 : Docker Compose Down
```powershell
docker-compose down
```

#### 10.3 Réinitialisation complète (optionnel)
Pour supprimer toutes les données :
```powershell
docker-compose down -v
```

---

## 🔍 Dépannage

### Problème : L'API ne répond pas

**Solution :**
```powershell
docker-compose logs backend
```
Vérifier les erreurs dans les logs.

### Problème : Données non chargées

**Solution :**
1. Vérifier que le fichier `data/Online Retail.xlsx` existe
2. Vérifier les logs : `docker-compose logs backend`
3. Redémarrer : `docker-compose restart backend`

### Problème : Analyse très lente

**Solutions :**
1. Augmenter le support minimum (ex: 0.02)
2. Réduire la taille du dataset
3. Allouer plus de RAM à Docker

---

## 📊 Résultats Attendus

### Avec Support = 0.01, Confiance = 0.5

**Itemsets :**
- Total : 200-500 itemsets
- Longueur 2 : ~150-300
- Longueur 3 : ~50-150
- Longueur 4+ : ~10-50

**Règles :**
- Total : 100-300 règles
- Confiance moyenne : 55-65%
- Lift moyen : 2.5-4.0

**Recommandations :**
- 5-10 recommandations par panier
- Confiance : 40-80%
- Lift : 2-6

---

## 🎓 Concepts Théoriques

### Algorithme FP-Growth

**Principe :**
1. Construction du FP-Tree (arbre de fréquence)
2. Extraction des itemsets fréquents par mining récursif
3. Génération des règles d'association

**Avantages :**
- ✅ Plus rapide qu'Apriori
- ✅ Pas de génération de candidats
- ✅ Deux passages sur les données seulement

**Complexité :**
- Temps : O(n × m) où n = transactions, m = items
- Espace : O(n × m) pour le FP-Tree

---

## 📚 Références

- **Dataset** : UCI Machine Learning Repository - Online Retail
- **Algorithme** : Han et al. (2000) - "Mining Frequent Patterns without Candidate Generation"
- **Bibliothèque** : mlxtend - Machine Learning Extensions

---

## 👥 Auteurs

- **Student A**
- **Student Y**

**Institution :** École Hassania des Travaux Publics (EHTP)  
**Filière :** Génie Informatique  
**Module :** Intelligence Artificielle Multi-Agents  
**Date :** Novembre 2025

---

**Bonne analyse ! 🚀**
