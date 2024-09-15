from django.shortcuts import render, redirect, get_object_or_404
from .forms import UtilisateurForm, TicketForm, PaiementForm, ConnexionForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from .models import Ticket, Sport, Utilisateur, Paiement, GenerationTicket
import locale

# Création de 'home'
def home(request):
    return render(request, 'home.html')

# Création de 'inscription'
def inscription(request):
    if request.method == 'POST':
        form = UtilisateurForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])  # Assure-toi d'enregistrer le mot de passe correctement
            user.save()
            return redirect('connexion')  # Redirige vers la page de connexion après l'inscription
    else:
        form = UtilisateurForm()
    return render(request, 'inscription.html', {'form': form})

# Vue pour la création de tickets
@login_required(login_url='connexion')
def ticket_create_view(request):
    sport_nom = request.GET.get('sport', '')  
    sport = Sport.objects.filter(nom=sport_nom).first()

    if sport:
        date_evenement = sport.date_evenement
    else:
        date_evenement = None

    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)  # Ne sauvegarde pas encore le ticket dans la base de données
            ticket.utilisateur = request.user  # Associe le ticket à l'utilisateur connecté
            ticket.save()  # Maintenant, on peut sauvegarder le ticket
            return redirect('panier')  # Redirige vers la page du panier
    else:
        initial_data = {'sport': sport}
        form = TicketForm(initial=initial_data)

    return render(request, 'ticket.html', {'form': form, 'date_evenement': date_evenement})


# Affichage de la liste des tickets
@login_required(login_url='connexion')
def ticket_list_view(request):
    tickets = Ticket.objects.all()
    return render(request, 'ticket_list.html', {'tickets': tickets})

# Mise à jour d'un ticket
@login_required(login_url='connexion')
def ticket_update_view(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)  
    if request.method == "POST":
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('ticket_list') 
    else:
        form = TicketForm(instance=ticket)  
    return render(request, 'ticket.html', {'form': form}) 

# Suppression d'un ticket 
@login_required(login_url='connexion')
def ticket_delete_view(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, utilisateur=request.user) 
    if request.method == "POST":
        ticket.delete()  
        return redirect('panier')  
    return render(request, 'ticket_confirm_delete.html', {'ticket': ticket})


#Récupérer la date de l'événement
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')  

def get_sport_date(request, sport_id):
    try:
        sport = Sport.objects.get(id=sport_id)
        formatted_date = sport.date_evenement.strftime('%d %B %Y')
        print(f"Date formatée : {formatted_date}")
        return JsonResponse({'date_evenement': formatted_date})
    except Sport.DoesNotExist:
        print(f"Sport avec ID {sport_id} non trouvé.")
        return JsonResponse({'error': 'Sport non trouvé'}, status=404)
    
#Liste des sports
def sport_list_view(request):
    sports = Sport.objects.all()
    return render(request, 'sport.html', {'sports': sports})

# Vue du panier
# @login_required(login_url='connexion')
# def panier_view(request):
#     utilisateur = request.user
#     tickets = Ticket.objects.filter(utilisateur=utilisateur)

#     if request.method == 'POST':
#         action = request.POST.get('action')

#         if action.startswith('delete_'):
#             # Supprimer le ticket
#             ticket_id = action.split('_')[1]
#             ticket = get_object_or_404(Ticket, id=ticket_id, utilisateur=request.user)
#             ticket.delete()
#             messages.success(request, 'Ticket supprimé avec succès.')
#             return redirect('panier')

#         elif action == 'update':
#             # Mettre à jour les quantités
#             for ticket in tickets:
#                 quantite_str = request.POST.get(f'quantite_{ticket.id}')
#                 if quantite_str and quantite_str.isdigit():
#                     quantite = int(quantite_str)
#                     if quantite > 0:
#                         ticket.quantite = quantite
#                         ticket.save()
#             messages.success(request, 'Quantités mises à jour avec succès.')

#         elif action == 'pay':
#             # Gestion du paiement
#             form = PaiementForm(request.POST)
#             if form.is_valid():
#                 total = sum(ticket.get_prix() * ticket.quantite for ticket in tickets)  # Recalculer le total avec les quantités
#                 paiement = form.save(commit=False)
#                 paiement.montant = total
#                 paiement.save()

#                 # Associer les tickets au paiement et générer les billets
#                 for ticket in tickets:
#                     ticket.paiements.add(paiement)
#                     ticket.save()

#                     # Générer un billet pour chaque ticket
#                     generation_ticket = GenerationTicket(ticket=ticket)
#                     generation_ticket.save()

#                 messages.success(request, 'Paiement effectué et billets générés avec succès.')
#                 return redirect('confirmation')

#     # Recalculer le total après la mise à jour des quantités
#     tickets = Ticket.objects.filter(utilisateur=utilisateur)  # Rafraîchir la liste des tickets
#     total = sum(ticket.get_prix() * ticket.quantite for ticket in tickets)  # Calcul du total avec les quantités
#     form = PaiementForm(initial={'montant': total})

#     return render(request, 'panier.html', {'tickets': tickets, 'total': total, 'form': form})

@login_required(login_url='connexion')
def panier_view(request):
    utilisateur = request.user
    tickets = Ticket.objects.filter(utilisateur=utilisateur)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action.startswith('delete_'):
            # Supprimer le ticket
            ticket_id = action.split('_')[1]
            ticket = get_object_or_404(Ticket, id=ticket_id, utilisateur=request.user)
            ticket.delete()
            messages.success(request, 'Ticket supprimé avec succès.')
            return redirect('panier')

        elif action == 'update':
            # Mettre à jour les quantités
            for ticket in tickets:
                quantite_str = request.POST.get(f'quantite_{ticket.id}')
                if quantite_str and quantite_str.isdigit():
                    quantite = int(quantite_str)
                    if quantite > 0:
                        ticket.quantite = quantite
                        ticket.save()
            messages.success(request, 'Quantités mises à jour avec succès.')

        elif action == 'pay':
            # Rediriger vers la page de paiement
            return redirect('paiement')  # Utiliser la vue de paiement pour gérer le paiement

    # Recalculer le total après les mises à jour
    tickets = Ticket.objects.filter(utilisateur=utilisateur)
    total = sum(ticket.get_prix() * ticket.quantite for ticket in tickets)
    form = PaiementForm(initial={'montant': total})

    return render(request, 'panier.html', {'tickets': tickets, 'total': total, 'form': form})


# Vue pour la connexion
class ConnexionView(LoginView):
    template_name = 'connexion.html'
    form_class = ConnexionForm

    def form_valid(self, form):
        # Vérifier l'authentification
        print(f"Authentification réussie pour : {form.get_user()}")
        return super().form_valid(form)

    def get_success_url(self):
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        return next_url or reverse_lazy('home')

# Vue pour la déconnexion
class DeconnexionView(LogoutView):
    next_page = 'home'
    
# Vue pour le paiement
@login_required(login_url='connexion')
def payment_view(request):
    utilisateur = request.user
    tickets = Ticket.objects.filter(utilisateur=utilisateur)
    total = sum(ticket.get_prix() for ticket in tickets)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'simulate':
            # Créer une instance du modèle Paiement pour la simulation
            paiement = Paiement.objects.create(
                ticket=tickets.first(),  # Associer un ticket (arbitraire dans le cas de simulation)
                montant=total,
                methode_paiement='Simulation',
                statut_paiement=True  # Marquer comme payé pour la simulation
            )
            
            # Générer les billets
            for ticket in tickets:
                GenerationTicket.objects.create(ticket=ticket)

            messages.success(request, 'Paiement simulé avec succès et billets générés !')
            return redirect('confirmation')

        elif action == 'pay':
            # Vérifier les champs de paiement
            card_number = request.POST.get('cardNumber')
            expiry_date = request.POST.get('expiryDate')
            cvv = request.POST.get('cvv')
            
            if card_number and expiry_date and cvv:
                # Créer une instance du modèle Paiement pour le paiement réel
                paiement = Paiement.objects.create(
                    ticket=tickets.first(),  # Associer un ticket (arbitraire pour l'exemple)
                    montant=total,
                    methode_paiement='Carte de crédit',
                    statut_paiement=True  # Marquer comme payé
                )
                
                # Générer les billets
                for ticket in tickets:
                    GenerationTicket.objects.create(ticket=ticket)

                messages.success(request, 'Paiement réussi et billets générés !')
                return redirect('confirmation')
            else:
                messages.error(request, 'Veuillez remplir tous les champs pour le paiement.')
    
    return render(request, 'paiement.html', {'total': total})

