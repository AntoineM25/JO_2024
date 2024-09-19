from django.test import TestCase
from jo_app.models import Utilisateur, Sport, Ticket, Paiement, GenerationTicket, Offre

## TEST DES MODELS ##

from django.core.exceptions import ValidationError

# Test du modèle Utilisateur
class UtilisateurModelTest(TestCase):

    def setUp(self):
        # Crée un utilisateur pour les tests
        self.utilisateur = Utilisateur.objects.create(
            nom='Dupont',
            prenom='Gilles',
            sexe='H',
            email='gilles.dupont@exemple.com',
            adresse='123 Rue Test',
            code_postal='75000',
            ville='Paris',
            date_de_naissance='1942-08-01'
        )

    def test_creation_utilisateur(self):
        # Vérifie que l'utilisateur a été créé avec les bons attributs
        utilisateur = Utilisateur.objects.get(email='gilles.dupont@exemple.com')
        self.assertEqual(utilisateur.nom, 'Dupont')
        self.assertEqual(utilisateur.prenom, 'Gilles')
        self.assertEqual(utilisateur.sexe, 'H')
        self.assertEqual(utilisateur.adresse, '123 Rue Test')
        self.assertEqual(utilisateur.code_postal, '75000')
        self.assertEqual(utilisateur.ville, 'Paris')
        self.assertEqual(str(utilisateur.date_de_naissance), '1942-08-01')

    def test_email_unique(self):
        # Vérifie que l'email de l'utilisateur est unique
        with self.assertRaises(Exception):
            Utilisateur.objects.create(
                nom='Dupont',
                prenom='Jean',
                sexe='H',
                email='gilles.dupont@exemple.com',  # Même email que l'utilisateur existant
                adresse='456 Rue Duplication',
                code_postal='75001',
                ville='Paris',
                date_de_naissance='1985-05-23'
            )

    def test_cle_securisee_generation(self):
        # Vérifie que la clé sécurisée est automatiquement générée
        self.assertIsNotNone(self.utilisateur.cle_securisee_1)
        self.assertEqual(len(self.utilisateur.cle_securisee_1), 64)

    def test_champs_obligatoires(self):
        # Vérifie que la création d'un utilisateur sans nom lève une exception
        with self.assertRaises(ValidationError):
            utilisateur = Utilisateur(
                prenom='SansNom',
                sexe='H',
                email='sans.nom@example.com'
            )
            utilisateur.full_clean()  # Utilisé pour déclencher les validations

    def test_validation_mot_de_passe(self):
        # Vérifie la validation du mot de passe si tu utilises une fonction de validation
        try:
            self.utilisateur.set_password('MotdePasse1!')
            self.utilisateur.full_clean()
        except ValidationError as e:
            self.fail(f"Le mot de passe n'a pas été validé correctement: {e}")


# Test du modèle Ticket
class TicketModelTest(TestCase):

    def setUp(self):
        # Création d'un utilisateur, d'un sport et d'une offre pour les tests
        self.utilisateur = Utilisateur.objects.create(
            nom='Dupont',
            prenom='Gilles',
            sexe='H',
            email='gilles.dupont@exemple.com',
            adresse='123 Rue Test',
            code_postal='75000',
            ville='Paris',
            date_de_naissance='1942-08-01'
        )
        
        self.sport = Sport.objects.create(
            nom='Basketball',
            date_evenement='2024-08-01'
        )

        self.offre = Offre.objects.create(
            type='solo',
            prix=20.00
        )

    def test_creation_ticket(self):
        # Création du ticket pour l'utilisateur, l'offre et le sport
        ticket = Ticket.objects.create(
            utilisateur=self.utilisateur,
            sport=self.sport,
            offre=self.offre,
            quantite=2
        )
        # Vérification si le ticket a été créé avec les bons attributs
        self.assertEqual(ticket.utilisateur.email, 'gilles.dupont@exemple.com')
        self.assertEqual(ticket.sport.nom, 'Basketball')
        self.assertEqual(ticket.offre.type, 'solo')
        self.assertEqual(ticket.quantite, 2)

    def test_calcul_prix_total_ticket(self):
        # Création du ticket pour tester le calcul du prix total
        ticket = Ticket.objects.create(
            utilisateur=self.utilisateur,
            sport=self.sport,
            offre=self.offre,
            quantite=3
        )
        # Vérification du prix total
        self.assertEqual(ticket.get_prix_total(), 60.00)  # 20.00 (prix de l'offre) * 3 (quantité)

        
# Test du modèle Sport
class SportModelTest(TestCase):

    def setUp(self):
        # Création du sport pour les tests
        self.sport = Sport.objects.create(
            nom='Natation',
            date_evenement='2024-07-25',
            description='Compétition de natation olympique.'
        )

    def test_creation_sport(self):
        # Vérification que le sport a bien été créé avec les bons attributs
        sport = Sport.objects.get(nom='Natation')
        self.assertEqual(sport.nom, 'Natation')
        self.assertEqual(str(sport.date_evenement), '2024-07-25')
        self.assertEqual(sport.description, 'Compétition de natation olympique.')
        # Vérifie que le champ image est vide par défaut
        self.assertFalse(sport.image)  # Renvoie False si l'image n'a pas été définie

    def test_str_representation(self):
        # Vérification de la représentation en chaîne du modèle
        self.assertEqual(str(self.sport), 'Natation')


# Test du modèle Paiement
class PaiementModelTest(TestCase):

    def setUp(self):
        # Création d'un utilisateur, un sport, et un ticket pour le paiement
        self.utilisateur = Utilisateur.objects.create(
            nom='Dupont',
            prenom='Gilles',
            sexe='H',
            email='gilles.dupont@exemple.com',
            adresse='123 Rue Test',
            code_postal='7500',
            ville='Paris',
            date_de_naissance='1942-08-01'
        )
        self.sport = Sport.objects.create(
            nom='Football',
            date_evenement='2024-09-15'
        )
        self.ticket = Ticket.objects.create(
            utilisateur=self.utilisateur,
            sport=self.sport,
            type_ticket='famille',
            quantite=1
        )

    def test_creation_paiement(self):
        # Création d'un paiement pour le ticket
        paiement = Paiement.objects.create(
            ticket=self.ticket,
            montant=self.ticket.get_prix(),
            methode_paiement='Carte de crédit',
            statut_paiement=True
        )
        # Vérification que le paiement a bien été créé avec les bons attributs
        self.assertEqual(paiement.ticket, self.ticket)
        self.assertEqual(paiement.montant, self.ticket.get_prix())
        self.assertEqual(paiement.methode_paiement, 'Carte de crédit')
        self.assertTrue(paiement.statut_paiement)

