# JO_2024

Ce projet est une application Django permettant la gestion de billets pour les événements sportifs des Jeux Olympiques de Paris 2024. Les utilisateurs peuvent s'inscrire, choisir leurs billets pour divers sports, gérer leur panier, et effectuer des paiements pour les billets sélectionnés.

## __Installation et configuration__

1. Cloner le dépôt :

```bash
git clone https://github.com/AntoineM25/JO_2024.git
```

2. Installer les dépendances :
Assurez-vous d'avoir Python et pip installés sur votre système. Ensuite, dans le dossier du projet, exécutez :
```bash
pip install -r requirements.txt
```

3. Configurer la base de données :

-   Ouvrez le fichier settings.py dans le dossier principal du projet.
-   Dans la section DATABASES, configurez les paramètres de connexion à votre base de données (nom, utilisateur, mot de passe, etc.).
-   Préparez les migrations pour créer les tables nécessaires dans la base de données :
```bash
python manage.py makemigrations
```
-   Appliquez ensuite les migrations :
```bash
python manage.py migrate
```

4. Lancer le serveur :
```bash
python manage.py runserver
```

## __Fonctionnalités principales__

-   Gestion des utilisateurs : inscription, connexion, déconnexion.
-   Gestion des billets : choix du type de billet (solo, duo, famille) et du sport, ajout au panier.
-   Gestion du panier : affichage des billets sélectionnés, mise à jour des quantités, suppression des billets.
-   Paiement simulé et génération de billets avec QR codes.
-   Interface d'administration pour gérer les utilisateurs, billets, sports, et paiements.

## __Tests__

### ***Tests manuels***

#### ***Models***

-   Test réalisé sur django/admin pour voir si chaque modèle est bien créé et contient les bons champs.
-   Amélioration des modèles grace à ces différents tests.
-   Création d'un utilisateur test, d'un ticket test, d'un paiement test, d'une génération de ticket test.
-   Ajout du modèle Sport et vérification de la bonne implémentation.

#### ***Base de données***

-   Test réalisé sur le terminal avec MySQL, la base de données est bien implémentée suite à l'ajout d'utilisateurs via django/admin.
-   Vérification de la bonne implémentation du formulaire d'inscription dans la base de données.
-   Vérification implémentation de la BDD sports.
-   Vérification de la création d'un QR code avec la clé sécurisé 1 et 2 (Résultat : OK).
-   Test du QR code récupération de la clé sécurisée 1 de l'utilisateur Guillaume Masson. Récupération de toutes les clés sécurisées 2 de l'utilisateur Guillaume Masson. Vérification de la bonne concaténation dans le QR code (Résultat : OK).

![Test QR code](/jo_app/static/images/tests/test_qr_code.png)

#### ***Templates***

-   Test réalisé avec un template qui affiche du texte sur une page web, pour voir si tout s'affiche correctement.
-   Test du template "Home" suite à l'ajout de bootstrap.
-   Test du template "Sport" suite à l'ajout de bootstrap.
-   Test de la fonctionnalité de déconnexion.
-   Test de la fonctionnalité de connexion.
-   Test des différents icônes (hover et active) dans la navigation.

#### ***Formulaires***

-   Test du formulaire d'inscription en renseignant chaque case.
-   Test du formulaire d'inscription sur chaque champ, pour valider que tous les champs sont obligatoires.
-   Test du formulaire de "Choix du billet" et vérification que le billet soit synchronisé au bon prix.
-   Test du formulaire de connexion
-   Test du formulaire de choix de ticket pour s'assurer que la synchronisation est bien réalisée avec le panier.

### ***Tests qualité du code***

#### Tests avec pylint
-   Amélioration de la note du code sous pylint : Your code has been rated at 3.11/10 (previous run: 2.90/10, +0.21)
-   Amélioration de la note du code sous pylint : Your code has been rated at 3.20/10 (previous run: 3.11/10, +0.09)
-   Amélioration de la note du code sous pylint : Your code has been rated at 3.66/10 (previous run: 3.40/10, +0.25)

### ***Tests unitaires***

-   L'application comporte des tests unitaires pour vérifier le bon fonctionnement des principales fonctionnalités.

#### Tests Disponibles

- **Modèles : Création d'un utilisateur** : Vérifie si un utilisateur est correctement créé avec les attributs attendus. 
- **Modèles : Validation de l'unicité de l'email** : Assure que deux utilisateurs ne peuvent pas avoir la même adresse email. 
- **Modèles : Création d'un ticket** : Vérifie si le ticket a été créé avec les bons attributs et que le calcul du prix est OK.
- **Modèles : Création d'un sport** : Vérifie la création d'un sport et la cohérence de ses attributs.
- **Modèles : Paiement** : Vérifie la création d'un paiement et que le statut du paiement soit correctement enregistré.
- **Modèles : Génération d'un ticket** : Vérification de la concaténation des clés sécurisées dans les QR codes.
-   Fonction : Validation du mot de passe : Vérifie que la validation du mot de passe impose un mot de passe de 8 caractères minimum, avec au moins une majuscule et un caractère spécial.
-   Formulaires : Inscription d'un utilisateur : Vérifie que le formulaire d'inscription d'un utilisateur est valide avec des données correctes et que les mots de passe sont vérifiés et hashés correctement.
-   Formulaires : Création d'un ticket : Vérifie si le formulaire de création de ticket initialise correctement les valeurs et valide les entrées utilisateur.
-   Formulaires : Paiement : Vérifie si le formulaire de paiement accepte des données valides et vérifie les choix de méthode de paiement.
-   Formulaires : Connexion : Teste la validation du formulaire de connexion avec des données valides et invalides.
-   Vues : Affichage de la page d'accueil : Vérifie que la page d'accueil est accessible et qu'elle utilise le bon template.
-   Vues : Inscription d'un utilisateur : Vérifie que l'utilisateur peut s'inscrire et qu'il est redirigé vers la page de connexion après une inscription réussie.
-   Vues : Création d'un ticket : Teste si un utilisateur connecté peut accéder à la vue de création de ticket et créer un ticket avec des données valides.
-   Vues : Liste des tickets : Vérifie si la liste des tickets est correctement affichée pour un utilisateur connecté.
-   Vues : Panier : Vérifie l'accès au panier, la mise à jour des quantités de tickets et la suppression des tickets du panier.
-   Vues : Téléchargement de billet : Vérifie l'accès et le téléchargement des billets générés sous forme de fichier PDF avec le QR code.

#### Exécution des Tests

Pour exécuter les tests unitaires, utilisez la commande suivante :

```bash
python manage.py test jo_app.tests
```
Exemple de sortie :

```bash
Found 6 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
......
----------------------------------------------------------------------
Ran 6 tests in 0.019s

OK
Destroying test database for alias 'default'...
```

## __Bug__

### ***Templates***

-   Bug en choisissant un sport : la date de l’événement n’était pas pris en compte sur le formulaire de choix des tickets. Ce bug a été résolue en rajoutant {{ date_evenement }}, manquant dans le template ticket.

- Impossible de se connecter une fois inscrit : 

![Bug Connexion](/jo_app/static/images/bugs/bug_connexion.png)

Ce bug a été résolu en ajoutant la validation du mot de passe lors de l'inscription dans le model Utilisateur et "clean_password1" dans le formulaire d'inscription.

- Bug d'affichage des images dans la page Sport. Solution : ajout de {% load static %} dans le code

### ***Views***

-   Petit problème lorsque l'utilisateur se connecte depuis la page "Choix du billet" ou "Panier". Il était directement renvoyé sur la page d'accueil ce qui dégradait légèrement son experience utilisateur. Solution : Ajustement de "def get_success_url(self)" en ajoutant "next_url".

### ***Models***

-   Problème de somme dans le Panier. Il y avait un doublon dans les calculs du prix des billets entre le "Model" et la "View". Solution : MAJ du model Ticket.

## __Améliorations__

### ***Paiement***

-   Pour ce rendu je suis parti sur une simulation de paiement pour une carte bancaire. Pour améliorer la partie Paiement du site, il serait intéressant d'ajouter les fonctionnalités pour Paypal et pour un Virement bancaire.

## __Technologies utilisées__

### ***Langages***

-   [Python](https://www.python.org/)
-   [HTML](https://developer.mozilla.org/fr/docs/Web/HTML)
-   [CSS](https://developer.mozilla.org/fr/docs/Web/CSS)
-   [JavaScript](https://developer.mozilla.org/fr/docs/Web/JavaScript)

### ***Frameworks***

-   [Django](https://www.djangoproject.com/)
-   [Bootstrap](https://getbootstrap.com/)

### ***Librairies***

-   [Weasyprint](https://weasyprint.org/)

### ***Autres***

-   [Font Awesome](https://fontawesome.com/)
-   [FontIcon](https://gauger.io/fonticon/)
-   [GPT image generator ](https://chatgpt.com/g/g-pmuQfob8d-image-generator)