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