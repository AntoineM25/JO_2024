from django.shortcuts import render, redirect
from .forms import UtilisateurForm, TicketForm

# Création de la vue 'home'
def home(request):
    return render(request, 'home.html')

# Création de la vue 'inscription'
def inscription(request):
    if request.method == 'POST':
        form = UtilisateurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UtilisateurForm()

    return render(request, 'inscription.html', {'form': form})

# Création de la vue 'ticket'
def ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else: 
        form = TicketForm()
    
    return render(request, 'ticket.html', {'form': form})

# Lecture de la vue 'ticket'
def ticket(request):
    return render(request, 'ticket.html')
