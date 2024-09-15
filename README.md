# JO_2024

## __Testing__

### ***Tests manuels***

#### ***Models***

-   Test réalisé sur django/admin pour voir si chaque modèle est bien créé et contient les bons champs
-   Amélioration des modèles grace à ces différents tests
-   Création d'un utilisateur test, d'un ticket test, d'un paiement test, d'une génération de ticket test
-   Ajout du modèle Sport et vérification de la bonne implémentation 

#### ***Base de données***

-   Test réalisé sur le terminal avec MySQL, la base de données est bien implémentée suite à l'ajout d'utilisateurs via django/admin.
-   Vérification de la bonne implémentation du formulaire d'inscription dans la BDD
-   Vérification implémentation de la BDD sports
-   Vérification de la création d'un QR code avec la clé sécurisé 1 et 2 (Résultat : OK)

- Test du QR code récupération de la clé sécurisée 1 de l'utilisateur Guillaume Masson. Récupération de toutes les clés sécurisées 2 de l'utilisateur Guillaume Masson. Vérification de la bonne concaténation dans le QR code. Résultat : OK

![Test QR code](/jo_projet/jo_app/static/images/tests/test_qr_code.png)

#### ***Templates***

-   Test réalisé avec un template qui affiche du texte sur une page web, pour voir si tout s'affiche correctement
-   Test du template "Home" suite à l'ajout de bootstrap 
-   Test du template "Sport" suite à l'ajout de bootstrap 
-   Test de la fonctionnalité de déconnexion
-   Test de la fonctionnalité de connexion
-   Test des différents icônes (hover et active) dans la navigation

#### ***Formulaires***

-   Test du formulaire d'inscription en renseignant chaque case
-   Test du formulaire d'inscription sur chaque ligne, pour valider le fait qu'il faut obligatoirement renseigner chaque case
-   Test du formulaire de Choix du billet et vérification qu'un choix de billet soit synchronisé au bon prix 
-   Test du formulaire de connexion
-   Test du formulaire de choix de ticket pour savoir si la synchronisation est bien réalisée avec le Panier



## __Bug__

### ***Templates***

-   Bug en choisissant un sport : la date de l’événement n’était pas pris en compte sur le formulaire de choix des tickets. Ce bug a été résolue en rajoutant {{ date_evenement }}, manquant dans le template ticket

- Impossible de se connecter une fois inscrit : 

![Bug Connexion](/jo_projet/jo_app/static/images/bugs/bug_connexion.png)

Ce bug a été résolu en ajoutant la validation du mot de passe lors de l'inscription dans le model Utilisateur et "clean_password1" dans le formulaire d'inscription

- Bug d'affichage des images dans la page Sport. Solution : ajout de {% load static %} dans le code

### ***Views***

- Petit problème lorsque l'utilisateur se connecte depuis la page "Choix du billet" ou "Panier". Il était directement renvoyé sur la page d'accueil ce qui dégradait légèrement son experience utilisateur. Solution : Ajustement de "def get_success_url(self)" en ajoutant "next_url"

### ***Models***
- Problème de somme dans le Panier. Il y avait un doublon dans les calculs du prix des billets entre le "Model" et la "View". Solution : MAJ du model Ticket

## __Améliorations__

### ***Paiement***
- Pour ce rendu je suis parti sur une simulation de paiement pour une carte bancaire. Pour améliorer la partie Paiement du site, il serait intéressant d'ajouter les fonctionnalités pour Paypal et pour un Virement bancaire 