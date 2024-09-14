from django.shortcuts import render, redirect, get_object_or_404
from .forms import UtilisateurForm, TicketForm, PaiementForm, ConnexionForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse
from django.urls import reverse_lazy
from .models import Ticket, Sport, Utilisateur
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

# Vue pour le panier
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

        elif action == 'pay':
            # Gestion du paiement
            form = PaiementForm(request.POST)
            if form.is_valid():
                total = sum(ticket.get_prix() for ticket in tickets)  # Recalculer le total ici
                paiement = form.save(commit=False)
                paiement.montant = total
                paiement.save()

                # Associer les tickets au paiement
                for ticket in tickets:
                    ticket.paiements.add(paiement)
                    ticket.save()

                return redirect('confirmation')

    # Recalculer le total après la mise à jour des quantités
    tickets = Ticket.objects.filter(utilisateur=utilisateur)  # Rafraîchir la liste des tickets
    total = sum(ticket.get_prix() for ticket in tickets)  # Calcul du total
    form = PaiementForm(initial={'montant': total})
    
    return render(request, 'panier.html', {'tickets': tickets, 'total': total, 'form': form})

# # Vue quantité MAJ du panier
# from django.http import JsonResponse

# @login_required(login_url='connexion')
# def update_ticket_quantity(request):
#     if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         ticket_id = request.POST.get('ticket_id')
#         quantite_str = request.POST.get('quantite')

#         try:
#             ticket = Ticket.objects.get(id=ticket_id, utilisateur=request.user)
#             quantite = int(quantite_str)
#             if quantite > 0:
#                 ticket.quantite = quantite
#                 ticket.save()
                
#                 # Recalculer le total du panier
#                 tickets = Ticket.objects.filter(utilisateur=request.user)
#                 total = sum(ticket.get_prix() for ticket in tickets)
                
#                 return JsonResponse({'success': True, 'total': total})
#             else:
#                 return JsonResponse({'success': False, 'error': 'Quantité invalide'})
#         except Ticket.DoesNotExist:
#             return JsonResponse({'success': False, 'error': 'Ticket non trouvé'})
#         except ValueError:
#             return JsonResponse({'success': False, 'error': 'Quantité non valide'})
#     return JsonResponse({'success': False, 'error': 'Requête invalide'})


    
# Vue pour la connexion
class ConnexionView(LoginView):
    template_name = 'connexion.html'
    form_class = ConnexionForm

    def form_valid(self, form):
        # Vérifier l'authentification
        print(f"Authentification réussie pour : {form.get_user()}")
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.GET.get('next', reverse_lazy('home'))

# Vue pour la déconnexion
class DeconnexionView(LogoutView):
    next_page = 'home'