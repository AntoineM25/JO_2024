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
def sport_list_view(request):
    sports = [
        {"nom": "Judo"},
        {"nom": "Basketball"},
        {"nom": "Tennis"},
        {"nom": "Natation"},
        {"nom": "Athlétisme"},
    ]
    return render(request, 'sport.html', {'sports': sports})
    
"""
    # Liste des sports + dates des événements
def sport_list_view(request):
    sports = [
        {"nom": "Football", "date_evenement": "2024-06-10"},
        {"nom": "Basketball", "date_evenement": "2024-06-12"},
        {"nom": "Tennis", "date_evenement": "2024-06-15"},
        {"nom": "Natation", "date_evenement": "2024-06-18"},
        {"nom": "Athlétisme", "date_evenement": "2024-06-20"},
    ]
    return render(request, 'sport.html', {'sports': sports})
"""
# Création de 'ticket'
def ticket_create_view(request):
    sport = request.GET.get('sport', '') 

    # Correspondance entre les sports et leurs dates
    sport_dates = {
        'Judo': '2024-06-10',
        'Basketball': '2024-06-12',
        'Tennis': '2024-06-15',
        'Natation': '2024-06-18',
        'Athlétisme': '2024-06-20',
    }

    # Récupérer la date en fonction du sport sélectionné
    date_evenement = sport_dates.get(sport, '')  

    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ticket_list')
    else:
        initial_data = {
            'nom_evenement': sport,
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

