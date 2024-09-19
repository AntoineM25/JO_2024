from django.shortcuts import render, redirect, get_object_or_404
from .forms import UtilisateurForm, TicketForm, PaiementForm, ConnexionForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy, reverse
from .models import Ticket, Sport, Utilisateur, Paiement, GenerationTicket
from django.template.loader import render_to_string
from weasyprint import HTML
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
# @login_required(login_url='connexion')
# def ticket_list_view(request):
#     tickets = Ticket.objects.all()
#     return render(request, 'ticket_list.html', {'tickets': tickets})*
@login_required(login_url='connexion')
def ticket_list_view(request):
    tickets = Ticket.objects.all()
    tickets_list = ', '.join([str(ticket) for ticket in tickets])
    return HttpResponse(f"Liste des tickets: {tickets_list}")


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
    
# Liste des sports
def sport_list_view(request):
    sports = Sport.objects.all()
    return render(request, 'sport.html', {'sports': sports})

# Vue du panier
@login_required(login_url='connexion')
def panier_view(request):
    utilisateur = request.user
    # Filtrer uniquement les tickets non achetés
    tickets = Ticket.objects.filter(utilisateur=utilisateur, est_achete=False)

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
            return redirect('panier')

        elif action == 'pay':
            # Mettre à jour les quantités avant le paiement
            for ticket in tickets:
                quantite_str = request.POST.get(f'quantite_{ticket.id}')
                if quantite_str and quantite_str.isdigit():
                    quantite = int(quantite_str)
                    if quantite > 0:
                        ticket.quantite = quantite
                        ticket.save()

            # Rediriger vers la page de paiement avec le montant mis à jour
            return redirect('paiement')

    # Recalculer le total après la mise à jour des quantités
    total = sum(ticket.get_prix_total() for ticket in tickets)  # Calcul du total avec les quantités
    form = PaiementForm(initial={'montant': total})

    return render(request, 'panier.html', {'tickets': tickets, 'total': f"{total:.2f}€", 'form': form})

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
def paiement_view(request):
    utilisateur = request.user
    # Filtrer uniquement les tickets non achetés pour le calcul du paiement
    tickets = Ticket.objects.filter(utilisateur=utilisateur, est_achete=False)
    total = sum(ticket.get_prix_total() for ticket in tickets)  # Calcul du total avec les quantités

    if request.method == 'POST':
        # Simuler le paiement
        card_number = request.POST.get('cardNumber')
        expiry_date = request.POST.get('expiryDate')
        cvv = request.POST.get('cvv')
        
        if card_number and expiry_date and cvv:  # Vérification basique pour le mock
            # Générer les billets et marquer les tickets comme achetés
            for ticket in tickets:
                for _ in range(ticket.quantite):  # Créer une instance de GenerationTicket pour chaque billet
                    GenerationTicket.objects.create(ticket=ticket)
                ticket.est_achete = True
                ticket.save()
            
            # Afficher un message de succès
            messages.success(request, 'Paiement réussi et billets générés !')
            
            # Rediriger vers la page de confirmation
            return redirect('confirmation')
        else:
            messages.error(request, 'Veuillez remplir tous les champs pour le paiement.')

    return render(request, 'paiement.html', {'total': f"{total:.2f}€"})

# MAJ automatique des quantités du panier
@login_required(login_url='connexion')
def maj_quantite_view(request):
    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        quantite = request.POST.get('quantite')
        
        try:
            # Assurez-vous de filtrer les tickets non achetés
            ticket = Ticket.objects.get(id=ticket_id, utilisateur=request.user, est_achete=False)
            if quantite.isdigit() and int(quantite) > 0:
                ticket.quantite = int(quantite)
                ticket.save()
            else:
                return JsonResponse({'success': False, 'message': 'Quantité invalide.'})
        except Ticket.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Ticket non trouvé.'})

        # Recalculer le total du panier après la mise à jour de la quantité
        tickets = Ticket.objects.filter(utilisateur=request.user, est_achete=False)  # Filtrer les tickets non achetés
        total = sum(ticket.get_prix_total() for ticket in tickets)
        total_formatted = f"{total:.2f}€"  # Formater le total avec deux décimales

        return JsonResponse({'success': True, 'total': total_formatted})

    return JsonResponse({'success': False, 'message': 'Requête invalide.'})

# Vue de confirmation du paiement
def confirmation_view(request):
    return render(request, 'confirmation.html', {
        'message': 'Votre paiement a bien été effectué et vos billets ont été générés !'
    })

# Vue Mes commandes
@login_required(login_url='connexion')
def mes_commandes_view(request):
    utilisateur = request.user
    tickets = Ticket.objects.filter(utilisateur=utilisateur, est_achete=True)  # Filtrer uniquement les tickets achetés
    billets = GenerationTicket.objects.filter(ticket__utilisateur=utilisateur)
    
    return render(request, 'mes_commandes.html', {'tickets': tickets, 'billets': billets})

# Vue pour télécharger le billet en PDF
@login_required(login_url='connexion')
def telecharger_billet_view(request, billet_id):
    billet = get_object_or_404(GenerationTicket, id=billet_id, ticket__utilisateur=request.user)
    nom_fichier = f"Billet_{billet.ticket.sport.nom}_{billet.ticket.utilisateur.prenom}_{billet.ticket.utilisateur.nom}.pdf"
    qr_code_url = request.build_absolute_uri(billet.qr_code.url)
    html_string = render(request, 'billet_pdf.html', {'billet': billet, 'qr_code_url': qr_code_url}).content.decode('utf-8')
    html = HTML(string=html_string)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nom_fichier}"'
    html.write_pdf(response)
    
    return response

# Vue ventes pour admin
@login_required(login_url='connexion')
def ventes_view(request):
    billets = GenerationTicket.objects.all()
    
    return render(request, 'ventes.html', {'billets': billets})