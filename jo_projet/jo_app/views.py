from django.shortcuts import render, redirect, get_object_or_404
from .forms import UtilisateurForm, TicketForm
from .models import Ticket

# Création de 'home'
def home(request):
    return render(request, 'home.html')

# Création de 'inscription'
def inscription(request):
    if request.method == 'POST':
        form = UtilisateurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UtilisateurForm()
    return render(request, 'inscription.html', {'form': form})

# Page des sports
from .models import Sport

def sport_list_view(request):
    sports = Sport.objects.all()  # Récupérer tous les sports depuis la base de données
    return render(request, 'sport.html', {'sports': sports})
    
# Création de 'ticket'
def ticket_create_view(request):
    sport_nom = request.GET.get('sport', '')  # Récupérer le nom du sport sélectionné

    # Trouver le sport correspondant dans la base de données
    sport = Sport.objects.filter(nom=sport_nom).first()

    # Si le sport existe, on récupère sa date
    if sport:
        date_evenement = sport.date_evenement
    else:
        date_evenement = None

    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ticket_list')
    else:
        # Initialiser les données avec le sport et sa date
        initial_data = {
            'nom_evenement': sport_nom,
            'date_evenement': date_evenement,
        }
        form = TicketForm(initial=initial_data)

    return render(request, 'ticket.html', {'form': form})

# Affichage de la liste des tickets
def ticket_list_view(request):
    tickets = Ticket.objects.all()
    return render(request, 'ticket_list.html', {'tickets': tickets})

# Mise à jour d'un ticket
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

