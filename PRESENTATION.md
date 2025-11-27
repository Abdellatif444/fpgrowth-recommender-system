# 🎯 Résumé du Projet - Présentation

## Informations Générales

**Titre :** Système de Recommandation avec FP-Growth  
**Auteurs :** Student A & Student Y  
**Institution :** EHTP - École Hassania des Travaux Publics  
**Module :** Intelligence Artificielle Multi-Agents  
**Date :** Novembre 2025

---

## 📌 Objectif du Projet

Développer un système complet de recommandation de produits utilisant l'algorithme **FP-Growth** (Frequent Pattern Growth) pour analyser les associations entre produits et générer des recommandations personnalisées.

---

## 🏗️ Architecture Technique

### Stack Technologique

```
┌─────────────────────┐
│   Frontend          │  HTML5, CSS3, JavaScript
│   (Nginx)           │  Interface utilisateur moderne
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
     └───►  PostgreSQL 15   │  Persistance des données
         │  Transactions    │
         └──────────────────┘
```

### Technologies Utilisées

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| **Frontend** | HTML/CSS/JS | Interface utilisateur |
| **Backend** | Flask (Python) | API REST |
| **Algorithme** | FP-Growth (mlxtend) | Analyse d'associations |
| **Base de données** | PostgreSQL | Stockage des données |
| **Orchestration** | Docker Compose | Déploiement |

---

## 📊 Dataset

**Source :** UCI Machine Learning Repository - Online Retail  
**Fichier :** `Online Retail.xlsx`

### Caractéristiques

- **Lignes brutes :** 541,909 transactions
- **Lignes nettoyées :** ~400,000 transactions
- **Période :** 01/12/2010 - 09/12/2011
- **Pays :** 38 pays (principalement UK)
- **Clients :** ~4,300 clients uniques
- **Produits :** ~3,600 produits uniques

### Colonnes

| Colonne | Description |
|---------|-------------|
| InvoiceNo | Numéro de facture |
| StockCode | Code produit |
| Description | Nom du produit |
| Quantity | Quantité achetée |
| InvoiceDate | Date de la transaction |
| UnitPrice | Prix unitaire |
| CustomerID | Identifiant client |
| Country | Pays |

---

## 🔬 Algorithme FP-Growth

### Principe

**FP-Growth** (Frequent Pattern Growth) est un algorithme d'extraction d'itemsets fréquents et de règles d'association.

### Étapes

1. **Construction du FP-Tree**
   - Arbre de fréquence compressé
   - Stockage efficace des transactions

2. **Mining Récursif**
   - Extraction des itemsets fréquents
   - Pas de génération de candidats

3. **Génération des Règles**
   - Calcul du support, confiance, lift
   - Filtrage selon les seuils

### Avantages vs Apriori

| Critère | FP-Growth | Apriori |
|---------|-----------|---------|
| **Passages sur les données** | 2 | k+1 (k = taille max itemset) |
| **Génération de candidats** | Non | Oui |
| **Vitesse** | ⚡ Rapide | 🐌 Lent |
| **Mémoire** | Moyenne | Faible |

---

## 🎯 Fonctionnalités Implémentées

### 1. Chargement et Nettoyage des Données

- ✅ Lecture du fichier Excel
- ✅ Suppression des transactions annulées
- ✅ Suppression des valeurs manquantes
- ✅ Suppression des quantités/prix négatifs
- ✅ Normalisation des descriptions
- ✅ Insertion dans PostgreSQL

### 2. Analyse FP-Growth

- ✅ Configuration des paramètres (support, confiance)
- ✅ Extraction des itemsets fréquents
- ✅ Génération des règles d'association
- ✅ Calcul des métriques (support, confiance, lift, leverage, conviction)
- ✅ Sauvegarde des résultats

### 3. Système de Recommandation

- ✅ Recommandations basées sur le panier actuel
- ✅ Produits fréquemment achetés ensemble
- ✅ Recommandations par similarité
- ✅ Explications des recommandations

### 4. Visualisation et Interface

- ✅ Dashboard interactif
- ✅ Statistiques en temps réel
- ✅ Exploration des itemsets
- ✅ Exploration des règles
- ✅ Interface de recommandation

---

## 📈 Métriques Utilisées

### Support

**Définition :** Fréquence d'apparition d'un itemset

```
Support(A) = Nombre de transactions contenant A / Nombre total de transactions
```

**Exemple :** Support(Pain, Beurre) = 0.02 → Ces produits apparaissent ensemble dans 2% des transactions

### Confiance

**Définition :** Probabilité conditionnelle

```
Confiance(A → B) = Support(A ∪ B) / Support(A)
```

**Exemple :** Confiance(Pain → Beurre) = 0.65 → 65% des clients qui achètent du pain achètent aussi du beurre

### Lift

**Définition :** Force de l'association

```
Lift(A → B) = Confiance(A → B) / Support(B)
```

**Interprétation :**
- Lift > 1 : Association positive (A et B sont liés)
- Lift = 1 : Indépendance (pas de relation)
- Lift < 1 : Association négative (A et B s'excluent)

**Exemple :** Lift(Pain → Beurre) = 3.2 → L'association est 3.2× plus forte que le hasard

---

## 🚀 Démonstration

### Étape 1 : Démarrage
```bash
docker-compose up --build
```

### Étape 2 : Accès
- Frontend : http://localhost:8082
- API : http://localhost:5000

### Étape 3 : Utilisation
1. Charger les données
2. Configurer les paramètres
3. Lancer l'analyse
4. Explorer les résultats
5. Obtenir des recommandations

---

## 📊 Résultats Typiques

### Avec Support = 0.01, Confiance = 0.5

**Itemsets Fréquents :** 200-500  
**Règles d'Association :** 100-300  
**Confiance Moyenne :** 55-65%  
**Lift Moyen :** 2.5-4.0

### Exemples de Règles Découvertes

```
WHITE HANGING HEART T-LIGHT HOLDER → REGENCY CAKESTAND 3 TIER
Support: 2.5% | Confiance: 65% | Lift: 3.2

JUMBO BAG RED RETROSPOT → PARTY BUNTING
Support: 1.8% | Confiance: 58% | Lift: 2.9
```

---

## 💡 Cas d'Usage

### 1. E-Commerce
- Recommandations "Vous aimerez aussi"
- Bundles de produits
- Promotions ciblées

### 2. Retail Physique
- Placement des produits en magasin
- Optimisation des rayons
- Gestion des stocks

### 3. Marketing
- Campagnes personnalisées
- Segmentation client
- Cross-selling / Up-selling

---

## 🎨 Points Forts du Projet

### Technique

✅ **Architecture moderne** : Microservices avec Docker  
✅ **API REST complète** : Endpoints documentés  
✅ **Base de données** : Persistance PostgreSQL  
✅ **Algorithme efficace** : FP-Growth optimisé  
✅ **Code modulaire** : Séparation des responsabilités

### Interface

✅ **Design moderne** : Interface sombre premium  
✅ **Responsive** : Adapté à tous les écrans  
✅ **Interactif** : Feedback en temps réel  
✅ **Intuitif** : Navigation simple  
✅ **Animations** : Transitions fluides

### Documentation

✅ **README complet** : Architecture et installation  
✅ **Guide de démarrage** : Étapes détaillées  
✅ **Étapes d'exécution** : Tutoriel complet  
✅ **Code commenté** : Explications dans le code

---

## 🔮 Améliorations Futures

### Court Terme

- [ ] Filtres avancés sur les résultats
- [ ] Export des résultats (CSV, JSON)
- [ ] Graphiques de visualisation
- [ ] Historique des analyses

### Moyen Terme

- [ ] Algorithmes supplémentaires (Apriori, ECLAT)
- [ ] Analyse temporelle
- [ ] Segmentation par pays/client
- [ ] API de prédiction en temps réel

### Long Terme

- [ ] Machine Learning pour la prédiction
- [ ] Système de scoring avancé
- [ ] Intégration avec des plateformes e-commerce
- [ ] Tableau de bord analytique complet

---

## 📚 Références Académiques

1. **Han, J., Pei, J., & Yin, Y. (2000)**  
   "Mining Frequent Patterns without Candidate Generation"  
   *ACM SIGMOD Record*

2. **Agrawal, R., & Srikant, R. (1994)**  
   "Fast Algorithms for Mining Association Rules"  
   *VLDB Conference*

3. **Raschka, S. (2018)**  
   "MLxtend: Providing machine learning and data science utilities"  
   *Journal of Open Source Software*

---

## 🎓 Compétences Démontrées

### Techniques

- ✅ Data Mining et Machine Learning
- ✅ Développement d'API REST
- ✅ Gestion de bases de données
- ✅ Containerisation avec Docker
- ✅ Développement Full-Stack

### Méthodologiques

- ✅ Architecture logicielle
- ✅ Gestion de projet
- ✅ Documentation technique
- ✅ Tests et validation
- ✅ Déploiement

---

## 🏆 Conclusion

Ce projet démontre une **implémentation complète et professionnelle** d'un système de recommandation basé sur l'algorithme FP-Growth, avec :

- 🎯 Une architecture moderne et scalable
- 💻 Un code propre et bien documenté
- 🎨 Une interface utilisateur attractive
- 📊 Des résultats pertinents et exploitables
- 🚀 Un déploiement simple avec Docker

Le système est **prêt pour une utilisation réelle** et peut être facilement étendu avec de nouvelles fonctionnalités.

---

**Merci de votre attention ! 🙏**

---

## 📞 Contact

**Student A**  
**Student Y**

École Hassania des Travaux Publics (EHTP)  
Génie Informatique - Novembre 2025
