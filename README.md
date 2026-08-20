# 💊 PharmaNPS-Alou — Gestion de pharmacie

> Application web de gestion d'une pharmacie couvrant le **stock des médicaments**, les **ventes**, les **clients**, la **facturation** et le **suivi de l'activité commerciale**.

Le projet a été développé avec **Django** et déployé sur **Render** avec une base de données **PostgreSQL**.

L'objectif est de proposer une application permettant de centraliser les principales opérations quotidiennes d'une pharmacie dans une même interface.

> **🔗 Démo en ligne : [PharmaNPS-Alou](https://pharmanps-aloucoding-b8ex.onrender.com/)**

---

## 🎯 Présentation du projet

Une pharmacie doit gérer simultanément plusieurs types d'informations :

- les médicaments disponibles ;
- les quantités en stock ;
- les mouvements de stock ;
- les ventes ;
- les clients ;
- les paiements ;
- les factures ;
- les alertes de stock ;
- les indicateurs commerciaux.

PharmaNPS-Alou regroupe ces différents besoins dans une application web unique.

Le projet met particulièrement l'accent sur la **cohérence entre les ventes et le stock**.

Lorsqu'un médicament est vendu, le système peut notamment :

```text
Vente
  ↓
Création des lignes de vente
  ↓
Décrémentation du stock
  ↓
Création du mouvement de stock
  ↓
Mise à jour des indicateurs
  ↓
Génération de la facture
```

Cette logique permet d'éviter que les différentes parties de l'application fonctionnent indépendamment les unes des autres.

---

## 🖼️ Aperçu

| Accueil | Panier | Facture |
| :---: | :---: | :---: |
| ![Accueil](public/accueil.png) | ![Panier](public/panier.png) | ![Facture](public/facture.png) |

| Facture | Catégories | Chiffre d'affaires |
| :---: | :---: | :---: |
| ![Facture variante](public/facture-bis.png) | ![Catégories](public/categorie.png) | ![Chiffre d'affaires](public/chiffre-affaire.png) |

| Clients | Connexion | Médicaments |
| :---: | :---: | :---: |
| ![Clients](public/clients.png) | ![Connexion](public/login.png) | ![Médicaments](public/medicaments.png) |

---

## ✨ Fonctionnalités

### 🔐 Authentification

L'application dispose d'un système d'authentification permettant de :

- créer un compte ;
- se connecter ;
- se déconnecter ;
- accéder à un tableau de bord personnel.

Les fonctionnalités de gestion sont accessibles aux utilisateurs authentifiés.

---

### 💊 Gestion des médicaments

Chaque médicament peut être décrit avec plusieurs informations :

- nom ;
- DCI (Dénomination Commune Internationale) ;
- code-barres unique ;
- catégorie ;
- forme galénique ;
- dosage ;
- prix d'achat ;
- prix de vente ;
- quantité en stock ;
- seuil d'alerte ;
- date de péremption ;
- image.

Les médicaments sont organisés par catégories afin de faciliter leur gestion.

---

### 📦 Gestion du stock

L'application conserve l'historique des mouvements de stock.

Les différents types de mouvements pris en compte sont notamment :

- entrée ;
- sortie ;
- perte ;
- produit périmé ;
- ajustement.

Un `StockMovement` permet de conserver une trace des modifications effectuées sur le stock.

La logique métier assure également la mise à jour automatique de la quantité disponible.

---

### 🛒 Point de vente (POS)

Le module de vente permet de réaliser une vente directement depuis l'application.

Fonctionnalités principales :

- recherche instantanée des médicaments ;
- ajout de produits au panier ;
- gestion de plusieurs lignes ;
- calcul automatique du total ;
- calcul de la monnaie à rendre ;
- application d'une remise ;
- sélection du mode de paiement ;
- génération d'une facture.

La vente est également liée à la gestion du stock.

---

### 👥 Gestion des clients

Les clients peuvent être enregistrés avec différentes informations.

Le système distingue notamment :

- particulier ;
- entreprise ;
- assurance.

Le module prend également en charge :

- les points de fidélité ;
- le crédit client ;
- les coordonnées du client ;
- l'association entre client et vente.

---

### 📊 Tableau de bord

Le tableau de bord fournit une vision synthétique de l'activité.

Il permet notamment de consulter :

- le chiffre d'affaires du jour ;
- le chiffre d'affaires de la semaine ;
- le chiffre d'affaires du mois ;
- le chiffre d'affaires total ;
- les ventes récentes ;
- les produits les plus vendus ;
- les alertes de stock faible.

Des graphiques **Chart.js** permettent notamment de visualiser :

- les ventes des 7 derniers jours ;
- le top 5 des produits vendus.

---

## 🧠 Logique métier

Une partie importante du projet concerne la cohérence entre les différents modules.

### Vente et stock

Lorsqu'une vente est enregistrée :

```text
Sale
 │
 ├── SaleItem
 │     │
 │     ├── Médicament
 │     └── Quantité vendue
 │
 ├── Calcul du total
 │
 └── Mise à jour du stock
        │
        └── StockMovement
```

Un `SaleItem` décrémente le stock du médicament correspondant et crée également un mouvement de stock.

Cela permet de conserver une trace de l'opération.

---

### Contrôle du stock disponible

L'application vérifie également qu'une vente ne dépasse pas la quantité disponible.

Exemple :

```text
Stock disponible : 5
Quantité demandée : 8

        ↓

Vente refusée
```

Cette règle évite qu'une vente fasse passer le stock à une quantité incohérente.

---

### Numérotation des ventes

Chaque vente possède un numéro généré automatiquement selon un format similaire à :

```text
VYYYYMMDDxxxx
```

Exemple :

```text
V202603150001
```

Cela permet d'identifier facilement une vente et de retrouver sa facture.

---

## 🗃️ Modèles de données

### Application `medications`

#### `Category`

Représente une catégorie de médicaments.

Principales informations :

- nom ;
- description.

#### `Medication`

Représente un médicament.

Principales informations :

- nom ;
- DCI ;
- code-barres ;
- catégorie ;
- forme ;
- dosage ;
- prix d'achat ;
- prix de vente ;
- stock ;
- seuil d'alerte ;
- date de péremption ;
- image.

#### `StockMovement`

Trace les mouvements effectués sur le stock.

Types de mouvements :

```text
Entrée
Sortie
Perte
Périmé
Ajustement
```

---

### Application `sales`

#### `Customer`

Représente un client.

Le modèle prend notamment en charge :

- coordonnées ;
- type de client ;
- fidélité ;
- crédit.

#### `Sale`

Représente une vente.

Le modèle gère notamment :

- numéro de vente ;
- remise ;
- mode de paiement ;
- statut ;
- total ;
- monnaie.

#### `SaleItem`

Représente une ligne de vente.

Il permet de relier :

```text
Vente
  ↕
Médicament
```

et de gérer la quantité vendue.

#### `Prescription`

Représente une ordonnance associée à un client et éventuellement à une vente.

> Le modèle existe dans l'application mais son intégration dans l'interface utilisateur reste à finaliser. Il est actuellement principalement accessible depuis l'administration Django.

---

## 🧱 Stack technique

| Couche | Technologie |
|---|---|
| Backend | **Django 5.2.7** |
| Langage | **Python** |
| Base de données production | **PostgreSQL** |
| Base de données développement | **SQLite** |
| Frontend | **Django Templates** |
| CSS | **Tailwind CSS** |
| Graphiques | **Chart.js** |
| Stockage des médias | **Cloudinary** |
| Fichiers statiques | **WhiteNoise** |
| Serveur d'application | **Gunicorn** |
| Hébergement | **Render** |

---

## 🏗️ Architecture du projet

```text
pharmanps-alou/
│
├── pharmanps_alou/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── users/
│   └── Authentification et tableau de bord
│
├── medications/
│   ├── Médicaments
│   ├── Catégories
│   ├── Stock
│   └── management/
│       └── commands/
│           └── seed_data.py
│
├── sales/
│   ├── Point de vente
│   ├── Ventes
│   ├── Clients
│   └── Ordonnances
│
├── templates/
│   ├── base
│   ├── medications
│   ├── sales
│   └── users
│
├── static/
│   ├── CSS
│   └── ressources locales
│
├── build.sh
├── render.yaml
├── requirements.txt
└── manage.py
```

---

## 📂 Responsabilité des principales applications

| Module | Responsabilité |
|---|---|
| `users` | Authentification et tableau de bord |
| `medications` | Médicaments, catégories et stock |
| `sales` | Ventes, panier, clients et ordonnances |
| `templates` | Interface utilisateur |
| `static` | Ressources statiques |
| `build.sh` | Préparation et déploiement sur Render |

Cette organisation permet de séparer les différentes responsabilités fonctionnelles de l'application.

---

## 🚀 Installation locale

### 1. Cloner le dépôt

```bash
git clone https://github.com/NdeyePendaSarr/pharmanps-aloucoding.git
cd pharmanps-aloucoding
```

### 2. Créer un environnement virtuel

Sous Linux / macOS :

```bash
python -m venv venv
source venv/bin/activate
```

Sous Windows :

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Créer un fichier `.env` à la racine :

```dotenv
SECRET_KEY=change-me
DEBUG=True
```

Pour une configuration PostgreSQL locale, ajouter également la configuration correspondante.

### 5. Appliquer les migrations

```bash
python manage.py migrate
```

### 6. Charger les données de démonstration

```bash
python manage.py seed_data
```

La commande est conçue pour être **idempotente**.

### 7. Créer un administrateur

```bash
python manage.py createsuperuser
```

### 8. Lancer le serveur

```bash
python manage.py runserver
```

L'application sera disponible sur :

```text
http://127.0.0.1:8000/
```

---

## 🌍 Déploiement sur Render

L'application est déployée sur **Render** avec :

- un service web Django ;
- une base PostgreSQL ;
- Cloudinary pour le stockage des médias.

Le fichier :

```text
render.yaml
```

contient la configuration du service.

---

### Script de build

À chaque déploiement, `build.sh` exécute notamment les différentes étapes nécessaires au démarrage de l'application :

```text
Installation des dépendances
        ↓
Compilation de Tailwind CSS
        ↓
collectstatic
        ↓
Migrations Django
        ↓
Initialisation de l'administrateur
        ↓
Chargement des données de démonstration
```

Les commandes d'initialisation sont conçues pour être **idempotentes**, afin de pouvoir être exécutées plusieurs fois sans créer de données incohérentes.

---

### Variables d'environnement

Les principales variables nécessaires au déploiement sont :

```dotenv
SECRET_KEY=
DEBUG=False
DATABASE_URL=
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
ADMIN_USERNAME=
ADMIN_EMAIL=
ADMIN_PASSWORD=
```

---

## ☁️ Stockage des médias

Les images des médicaments peuvent être stockées avec **Cloudinary**.

L'application prévoit également un mécanisme de repli vers des ressources statiques locales lorsqu'une image distante n'est pas disponible.

```text
Image médicament
      │
      ▼
Cloudinary
      │
      └── indisponible
             ↓
       Image locale
```

---

## 🧪 Qualité & tests

Plusieurs scénarios métier ont été vérifiés directement avec le shell Django.

Les contrôles réalisés comprennent notamment :

- suppression d'un médicament déjà vendu ;
- tentative de vente dépassant le stock disponible ;
- réalisation d'une vente normale ;
- panier contenant plusieurs lignes du même produit ;
- cohérence des mouvements de stock ;
- calcul des montants de vente.

Les problèmes identifiés lors de ces vérifications ont été corrigés puis testés à nouveau.

---

## ⚠️ État actuel du projet

Le projet couvre actuellement les principales fonctionnalités nécessaires à la gestion quotidienne d'une pharmacie :

```text
Authentification
      ↓
Gestion des médicaments
      ↓
Gestion du stock
      ↓
Point de vente
      ↓
Clients
      ↓
Facturation
      ↓
Tableau de bord
```

Certaines fonctionnalités restent cependant à approfondir, notamment l'intégration complète des ordonnances et l'automatisation de certains tests.

---

## 🔮 Pistes d'amélioration

### 📋 Ordonnances

Finaliser l'intégration du modèle `Prescription` :

- vues ;
- URLs ;
- templates ;
- création et consultation depuis l'interface ;
- association avec les ventes.

### 📄 Pagination

Ajouter une pagination sur les listes :

- médicaments ;
- ventes ;
- clients.

### 📦 Filtres de stock

Ajouter des filtres dédiés :

- stock faible ;
- produits périmés ;
- produits bientôt périmés.

Une partie de ces filtres pourrait être directement effectuée avec l'ORM Django plutôt qu'après récupération des données.

### 🧪 Tests automatisés

Renforcer la couverture de tests sur les règles métier critiques :

- calcul du stock ;
- ventes ;
- mouvements de stock ;
- impossibilité de vendre au-delà du stock ;
- calcul des totaux ;
- gestion des remises ;
- fidélité ;
- crédit client.

### 🧹 Maintenance

Nettoyer et regrouper certains scripts de maintenance présents à la racine du projet :

```text
populate_db.py
check_duplicates.py
compare_stats.py
fix_encoding.py
```

---

## 🎓 Compétences mises en pratique

Ce projet m'a permis de mettre en pratique :

- développement backend avec Django ;
- conception d'applications web avec Python ;
- modélisation de données relationnelles ;
- utilisation de PostgreSQL ;
- conception de modèles Django ;
- gestion des relations entre entités ;
- authentification ;
- gestion des stocks ;
- conception d'un point de vente ;
- logique métier liée aux ventes ;
- génération de factures ;
- gestion des médias avec Cloudinary ;
- création de tableaux de bord ;
- visualisation de données avec Chart.js ;
- gestion des migrations ;
- déploiement avec Render ;
- configuration d'un environnement de production ;
- tests et vérification de scénarios métier.

---

## 🔗 Liens

**Application en ligne :**

https://pharmanps-aloucoding-b8ex.onrender.com/

**Dépôt GitHub :**

https://github.com/NdeyePendaSarr/pharmanps-aloucoding

---

## 👩‍💻 Auteure

**Ndeye Penda Sarr**

Développeuse Web Full-Stack · Business Intelligence & Data

---

© 2025 Ndeye Penda Sarr