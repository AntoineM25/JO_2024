from django.shortcuts import render, redirect, get_object_or_404
from .forms import UtilisateurForm, TicketForm, PaiementForm, ConnexionForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse
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

@login_required
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
@login_required
def ticket_list_view(request):
    tickets = Ticket.objects.all()
    return render(request, 'ticket_list.html', {'tickets': tickets})

# Mise à jour d'un ticket
@login_required
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

def ticket_delete_view(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == "POST":
        ticket.delete()  
        return redirect('ticket_list')  
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
@login_required
def panier_view(request):
    try:
        utilisateur = Utilisateur.objects.get(email=request.user.email)
        tickets = Ticket.objects.filter(utilisateur=utilisateur)
        total = sum(ticket.get_prix() for ticket in tickets)

        if request.method == 'POST':
            form = PaiementForm(request.POST)
            if form.is_valid():
                paiement = form.save(commit=False)
                paiement.montant = total
                paiement.save()
                return redirect('confirmation')
        else:
            form = PaiementForm(initial={'montant': total})

        return render(request, 'panier.html', {'tickets': tickets, 'total': total, 'form': form})
    except Utilisateur.DoesNotExist:
        return redirect('inscription')
    
# Vue pour la connexion
class ConnexionView(LoginView):
    template_name = 'connexion.html'
    form_class = ConnexionForm

# Vue pour la déconnexion
class DeconnexionView(LogoutView):
    next_page = 'home'