from django.shortcuts import render, redirect
from .forms import UtilisateurForm

# Définition de la vue 'home'
def home(request):
    return render(request, 'home.html')

# Définition de la vue 'inscription'
def inscription(request):
    if request.method == 'POST':
        form = UtilisateurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirection après inscription
    else:
        form = UtilisateurForm()

    return render(request, 'inscription.html', {'form': form})

