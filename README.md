# 💊 PharmaNPS-Alou

Application web de gestion de pharmacie (stock, ventes, clients) développée avec **Django**.
Déployée sur Render : https://pharmanps-aloucoding-b8ex.onrender.com/

---

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Stack technique](#stack-technique)
- [Structure du projet](#structure-du-projet)
- [Modèles de données](#modèles-de-données)
- [Installation locale](#installation-locale)
- [Déploiement (Render)](#déploiement-render)
- [⚠️ Bugs et problèmes identifiés](#️-bugs-et-problèmes-identifiés)
- [Pistes d'amélioration](#pistes-damélioration)

---

## Fonctionnalités

- **Authentification** : inscription, connexion, déconnexion, tableau de bord
- **Gestion des médicaments** : fiche produit (DCI, code-barres, forme galénique, dosage, prix, péremption), catégories, historique des mouvements de stock (entrée/sortie/perte/périmé/ajustement)
- **Point de vente (POS)** : recherche instantanée, panier, calcul automatique de la monnaie, génération de facture
- **Gestion clients** : particulier/entreprise/assurance, points de fidélité, système de crédit
- **Tableau de bord** : chiffre d'affaires (jour/semaine/mois/total), graphiques (Chart.js) des ventes des 7 derniers jours et du top 5 des produits vendus, alertes stock faible

## Stack technique

| Composant | Techno |
|---|---|
| Backend | Django 5.2.7 |
| Base de données | PostgreSQL (prod) / SQLite (dev) |
| Stockage médias | Cloudinary |
| Fichiers statiques | WhiteNoise |
| CSS | Tailwind CSS (compilé en CLI, pas de Node en prod) |
| Serveur d'application | Gunicorn |
| Hébergement | Render (web service + PostgreSQL) |

## Structure du projet

```
pharmanps-alou/
├── pharmanps_alou/      # Config Django (settings, urls, wsgi)
├── users/                # Authentification + dashboard
├── medications/          # Médicaments, catégories, stock
│   └── management/commands/seed_data.py   # Données de démo (idempotent)
├── sales/                # Point de vente, ventes, clients, ordonnances
├── templates/            # Templates HTML (base, medications, sales, users)
├── static/                # CSS (Tailwind), images locales des médicaments
├── build.sh               # Script de build Render (Tailwind, collectstatic, migrate, seed)
├── render.yaml             # Config du service Render
└── requirements.txt
```

## Modèles de données

**medications**
- `Category` — nom, description
- `Medication` — nom, DCI, code-barres (unique), catégorie, forme, dosage, prix d'achat/vente, stock, seuil d'alerte, péremption, image (Cloudinary + repli statique)
- `StockMovement` — trace chaque mouvement et **met à jour le stock automatiquement** à la sauvegarde

**sales**
- `Customer` — coordonnées, type, conditions médicales, fidélité, crédit
- `Sale` — numéro auto (`VYYYYMMDDxxxx`), remise, mode de paiement, statut, calcul auto du total et de la monnaie
- `SaleItem` — décrémente le stock du médicament et crée un `StockMovement` à la création
- `Prescription` — ordonnance liée à un client/une vente *(modèle présent mais non utilisé dans l'interface, voir plus bas)*

## Installation locale

```bash
git clone https://github.com/NdeyePendaSarr/pharmanps-aloucoding.git
cd pharmanps-aloucoding
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# .env à la racine :
# SECRET_KEY=change-me
# DEBUG=True

python manage.py migrate
python manage.py seed_data      # données de démo
python manage.py createsuperuser
python manage.py runserver
```

## Déploiement (Render)

`build.sh` s'exécute à chaque déploiement : installe les dépendances, compile Tailwind, `collectstatic`, `migrate`, puis `init_admin` (crée le superuser depuis les variables d'environnement `ADMIN_USERNAME` / `ADMIN_EMAIL` / `ADMIN_PASSWORD`, idempotent) et `seed_data` (idempotent également, ne remplit que si la base est vide).

Variables d'environnement à définir sur Render : `SECRET_KEY` (auto-générée par `render.yaml`), `DEBUG=False`, `DATABASE_URL` (liée à la base Postgres), `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`, `ADMIN_USERNAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`.

---

## ✅ Bugs corrigés dans cette version

J'ai parcouru l'ensemble du code (modèles, vues, templates, settings, scripts de build), testé plusieurs scénarios directement en shell Django, et corrigé les bugs les plus sérieux ci-dessous (chacun re-testé après correction). Les points 🟢 restent des suggestions d'amélioration non appliquées automatiquement.

### ✅ 0. Le stock était décrémenté DEUX FOIS à chaque vente (bug le plus grave, trouvé en testant les autres correctifs)

`SaleItem.save()` décrémentait `medication.quantity` **directement**, puis créait un `StockMovement` (type `'sortie'`) dont le `save()` **décrémente lui aussi** `medication.quantity` pour ce même type de mouvement. Résultat : chaque vente retirait deux fois la quantité vendue du stock réel (ex. vendre 3 unités faisait chuter le stock de 6). C'est ce mécanisme qui expliquait, en partie, le stock négatif du test initial (5 en stock, 999 vendus → -1993 = 5 − 999 − 999).

**Correctif appliqué :** `SaleItem.save()` ne touche plus `medication.quantity` lui-même ; c'est désormais uniquement `StockMovement.save()` qui fait foi pour tout ajustement de stock (vente, retour, perte, péremption, ajustement...), qu'il soit déclenché depuis une vente ou depuis le formulaire de mouvement de stock manuel.

### ✅ 1. Suppression d'un médicament lié à une vente → erreur 500 (bug confirmé)

Dans `medications/views.py`, `medication_delete` attrape `ProtectedError` pour afficher un message propre quand un médicament ne peut pas être supprimé (car protégé par `on_delete=models.PROTECT` dans `SaleItem`) :

```python
except ProtectedError:
    messages.error(request, f'Impossible de supprimer "{name}" ...')
```

Mais **`ProtectedError` n'est jamais importé** dans ce fichier. L'historique Git montre que ce `try/except` a été ajouté spécifiquement dans le commit *"Fix: 500 suppression medicament..."* — l'intention était bonne, mais l'import a été oublié, donc le correctif ne fonctionne pas : tenter de supprimer un médicament déjà vendu plante toujours avec une erreur serveur (`NameError`, testé et reproduit).

**Correctif appliqué :**
```python
from django.db.models import Q, ProtectedError
```
Re-testé : supprimer un médicament rattaché à une vente affiche maintenant bien le message d'erreur prévu, sans planter, et le médicament n'est pas supprimé.

### ✅ 2. Aucune vérification du stock disponible avant une vente (survente possible)

Ni `sales/views.py::create_sale`, ni `SaleItem.save()` ne vérifient que la quantité vendue ne dépasse pas le stock disponible avant de décrémenter. Le contrôle `max="${item.stock}"` n'existe que côté JavaScript dans `pos.html` — un simple appel direct à l'API `/api/create-sale/` (ou une requête concurrente de deux caissiers sur le même produit) suffit à le contourner.

Test effectué : médicament avec **5** en stock, vente créée pour une quantité de **999** → stock final : **-1993**. Le stock peut devenir négatif sans aucun avertissement.

**Correctif appliqué :** `create_sale` valide désormais `quantité demandée <= medication.quantity` (cumulée par médicament, au cas où le panier contiendrait deux lignes du même produit) **avant** de créer quoi que ce soit, et lève une erreur métier claire sinon. Testé : une survente est bloquée avec un message explicite (`"Stock insuffisant pour ... (disponible : X, demandé : Y)"`), le stock reste inchangé et aucune vente partielle n'est créée en base.

### ✅ 3. Pas de transaction atomique + pas de verrou dans `create_sale`

Toujours dans `create_sale` : la vente et ses lignes étaient créées une par une dans une boucle, sans transaction. Si une erreur survenait sur un article au milieu de la boucle (ex. `medication_id` invalide), les lignes déjà créées — et les décréments de stock associés — restaient en base, alors que le client recevait une erreur. Résultat possible : une vente incomplète et un stock déjà amputé, sans qu'aucune vente cohérente n'existe pour l'expliquer. De plus, sans verrou, deux ventes simultanées sur le même produit pouvaient toutes les deux passer la validation de stock avant que l'une des deux ne décrémente réellement (condition de course classique).

**Correctif appliqué :** toute la création de la vente est maintenant dans `with transaction.atomic():`, avec `Medication.objects.select_for_update()` pour verrouiller chaque médicament concerné le temps de la transaction — toute erreur annule proprement l'ensemble (vente + lignes + mouvements de stock), et deux ventes concurrentes sur le même produit sont désormais sérialisées plutôt que de se marcher dessus.

### ✅ 4. Affichage d'image incohérent entre les pages

`Medication.image_display` gère intelligemment trois cas (image Cloudinary → image statique locale de repli → aucune). `medication_list.html` et `medication_detail.html` l'utilisent correctement. Mais **le POS (`pos.html`)** et l'API `search_medication` utilisent directement `med.image` / `med.image.url`, sans passer par `image_display`. Résultat : un médicament qui affiche correctement sa photo dans la liste ou sa fiche détail retombe sur un simple dégradé de couleur dans le point de vente, dès lors qu'il n'a pas d'image Cloudinary uploadée (ce qui est le cas de tous les produits de démo, qui utilisent le repli statique).

**Correctif appliqué :** `pos.html` et la vue `search_medication` utilisent maintenant `med.image_display`, comme le reste du site.

### ✅ 5. `sales/admin.py` était vide

`Customer`, `Sale`, `SaleItem` et `Prescription` n'étaient pas enregistrés dans l'admin Django (contrairement à `medications/admin.py`). Impossible pour un administrateur de consulter/corriger une vente ou un client depuis `/admin/`.

**Correctif appliqué :** les quatre modèles sont maintenant enregistrés, avec les lignes de vente affichées en inline sur la fiche `Sale`.

### 🟡 6. Le modèle `Prescription` n'est relié à rien *(non corrigé — nécessite de concevoir l'interface)*

Le modèle existe (ordonnance, médecin, image, notes) mais il n'y a **ni vue, ni URL, ni template** pour le créer ou le consulter (il est désormais au moins visible/gérable depuis l'admin, voir point 5). C'est une fonctionnalité commencée puis jamais branchée à l'interface publique — je n'ai pas ajouté ces vues/templates faute de maquette/besoin précis exprimé, mais je peux le faire sur demande.

### ✅ 7. Validateurs de mot de passe contournés à l'inscription

`settings.py` configure `AUTH_PASSWORD_VALIDATORS` (longueur minimale, mots de passe communs, etc.), mais `register_view` appelait directement `User.objects.create_user(...)` sans jamais exécuter `validate_password()`. Ces règles ne s'appliquaient donc jamais sur le formulaire d'inscription public.

**Correctif appliqué :** `register_view` appelle désormais `validate_password()` avant de créer le compte et affiche les erreurs retournées (mot de passe trop court, trop commun, etc.).

### 🟢 8. Pas de pagination

`medication_list`, `sale_list` et `customer_list` chargent l'intégralité des enregistrements à chaque affichage. Sans souci avec les données de démo, mais ça deviendra lent avec un vrai historique de ventes.

### 🟢 9. Filtres de stock évalués en Python plutôt qu'en base

Dans `medication_list`, les filtres `stock=low/expired/expiring` transforment le queryset en liste Python (`[m for m in medications if m.is_low_stock]`) et recalculent la propriété pour chaque ligne au lieu de filtrer via l'ORM. Fonctionnel, mais inutilement coûteux dès que la table grossit, et incompatible avec une future pagination côté base de données.

### 🟢 10. Fichiers en double / obsolètes

`populate_db.py` (racine) et `medications/management/commands/seed_data.py` font quasiment la même chose — le second est explicitement décrit dans son docstring comme "la version qui fonctionne en production" du premier. `populate_db.py`, `check_duplicates.py`, `compare_stats.py` et `fix_encoding.py` semblent être des scripts de maintenance ponctuels qui traînent à la racine du dépôt ; à déplacer dans un dossier `scripts/` ou à supprimer s'ils ne servent plus.

### 🟢 11. Aucun test automatisé

`tests.py` est vide (contenu par défaut de `startapp`) dans les trois apps. Vu la logique métier sensible (calcul de stock, de monnaie, de totaux), quelques tests unitaires sur `SaleItem.save()`, `Sale.save()` et `StockMovement.save()` seraient du temps bien investi.

---

## Pistes d'amélioration

- Corriger les points 1 à 4 en priorité (impact direct sur la fiabilité des ventes et du stock)
- Ajouter `transaction.atomic()` + vérification de stock dans `create_sale`
- Enregistrer les modèles `sales` dans l'admin
- Soit finir l'intégration de `Prescription`, soit le retirer si non prioritaire
- Ajouter `django.contrib.auth.password_validation.validate_password()` dans `register_view`
- Ajouter pagination (`django.core.paginator.Paginator`) sur les listes
- Ajouter des tests sur la logique de stock/vente
