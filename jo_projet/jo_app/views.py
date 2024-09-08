from django.shortcuts import render

# Définition de la vue 'home'
def home(request):
    return render(request, 'home.html')
