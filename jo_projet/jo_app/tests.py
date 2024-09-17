from django.test import TestCase
from jo_app.models import Utilisateur, Sport, Ticket, Paiement, GenerationTicket

## TEST DES MODELS ##

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
            code_postal='7500',
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
        self.assertEqual(utilisateur.code_postal, '7500')
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

# Test du modèle Ticket
class TicketModelTest(TestCase):

    def setUp(self):
        # Création un utilisateur et un sport pour les tests
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
            nom='Basketball',
            date_evenement='2024-08-01'
        )

    def test_creation_ticket(self):
        # Création du ticket pour l'utilisateur et le sport
        ticket = Ticket.objects.create(
            utilisateur=self.utilisateur,
            sport=self.sport,
            type_ticket='solo',
            quantite=2
        )
        # Vérification si le ticket a été créé avec les bons attributs
        self.assertEqual(ticket.utilisateur.email, 'gilles.dupont@exemple.com')
        self.assertEqual(ticket.sport.nom, 'Basketball')
        self.assertEqual(ticket.type_ticket, 'solo')
        self.assertEqual(ticket.quantite, 2)

    def test_calcul_prix_ticket(self):
        # Création du ticket pour tester le calcul du prix
        ticket = Ticket.objects.create(
            utilisateur=self.utilisateur,
            sport=self.sport,
            type_ticket='duo',
            quantite=1
        )
        # Vérification du prix pour le type 'duo'
        self.assertEqual(ticket.get_prix(), 35.00)
        
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
