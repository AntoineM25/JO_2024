"""
Ce module contient les vues de l'application. 
Il contient les vues home, inscription, ticket_create_view, 
ticket_list_view, ticket_update_view, ticket_delete_view, 
get_sport_date, sport_list_view, panier_view, ConnexionView, 
DeconnexionView, paiement_view, maj_quantite_view, confirmation_view, 
mes_commandes_view, telecharger_billet_view, ventes_view.
"""

import locale

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count, F, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from weasyprint import HTML

from .forms import ConnexionForm, PaiementForm, TicketForm, UtilisateurForm
from .models import GenerationTicket, Sport, Ticket

try:
    locale.setlocale(locale.LC_ALL, "fr_FR.UTF-8")
except locale.Error:
    locale.setlocale(locale.LC_ALL, "C")


def home(request):
    """
    Crée la vue de la page d'accueil.
    """
    return render(request, "home.html")


def inscription(request):
    """
    Crée la vue pour l'inscription.
    """
    if request.method == "POST":
        form = UtilisateurForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            user.save()
            return redirect("connexion")
    else:
        form = UtilisateurForm()
    return render(request, "inscription.html", {"form": form})


@login_required(login_url="connexion")
def ticket_create_view(request):
    """
    Crée la vue pour la création d'un ticket.
    """
    sport_nom = request.GET.get("sport", "")
    sport = Sport.objects.filter(nom=sport_nom).first()

    if sport:
        date_evenement = sport.date_evenement
    else:
        date_evenement = None

    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.utilisateur = request.user
            ticket.save()
            return redirect("panier")
    else:
        initial_data = {"sport": sport}
        form = TicketForm(initial=initial_data)

    return render(
        request, "ticket.html", {"form": form, "date_evenement": date_evenement}
    )


@login_required(login_url="connexion")
def ticket_list_view(request):
    """
    Crée la vue pour la liste des tickets.
    """
    tickets = Ticket.objects.all()
    tickets_list = ", ".join([str(ticket) for ticket in tickets])
    return HttpResponse(f"Liste des tickets: {tickets_list}")


@login_required(login_url="connexion")
def ticket_update_view(request, ticket_id):
    """
    Crée la vue pour la mise à jour d'un ticket.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == "POST":
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect("ticket_list")
    else:
        form = TicketForm(instance=ticket)
    return render(request, "ticket.html", {"form": form})


@login_required(login_url="connexion")
def ticket_delete_view(request, ticket_id):
    """
    Crée la vue pour la suppression d'un ticket.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id, utilisateur=request.user)
    if request.method == "POST":
        ticket.delete()
        return redirect("panier")
    return render(request, "ticket_confirm_delete.html", {"ticket": ticket})


def get_sport_date(request, sport_id):
    """
    Récupère la date d'un événement
    """
    try:
        sport = Sport.objects.get(id=sport_id)
        formatted_date = sport.date_evenement.strftime("%d %B %Y")
        print(f"Date formatée : {formatted_date}")
        return JsonResponse({"date_evenement": formatted_date})
    except Sport.DoesNotExist:
        print(f"Sport avec ID {sport_id} non trouvé.")
        return JsonResponse({"error": "Sport non trouvé"}, status=404)


def sport_list_view(request):
    """
    Crée la vue pour la liste des sports.
    """
    sports = Sport.objects.all()
    return render(request, "sport.html", {"sports": sports})


@login_required(login_url="connexion")
def panier_view(request):
    """
    Crée la vue pour le panier.
    """
    utilisateur = request.user
    tickets = Ticket.objects.filter(utilisateur=utilisateur, est_achete=False)

    if request.method == "POST":
        action = request.POST.get("action")

        if action.startswith("delete_"):
            ticket_id = action.split("_")[1]
            ticket = get_object_or_404(Ticket, id=ticket_id, utilisateur=request.user)
            ticket.delete()
            messages.success(request, "Ticket supprimé avec succès.")
            return redirect("panier")

        elif action == "update":
            for ticket in tickets:
                quantite_str = request.POST.get(f"quantite_{ticket.id}")
                if quantite_str and quantite_str.isdigit():
                    quantite = int(quantite_str)
                    if quantite > 0:
                        ticket.quantite = quantite
                        ticket.save()
            messages.success(request, "Quantités mises à jour avec succès.")
            return redirect("panier")

        elif action == "pay":
            for ticket in tickets:
                quantite_str = request.POST.get(f"quantite_{ticket.id}")
                if quantite_str and quantite_str.isdigit():
                    quantite = int(quantite_str)
                    if quantite > 0:
                        ticket.quantite = quantite
                        ticket.save()

            return redirect("paiement")

    total = sum(ticket.get_prix_total() for ticket in tickets)
    form = PaiementForm(initial={"montant": total})

    return render(
        request, "panier.html", {"tickets": tickets, "total": total, "form": form}
    )


class ConnexionView(LoginView):
    """
    Vue pour l'authentification.
    """
    template_name = "connexion.html"
    form_class = ConnexionForm

    def form_valid(self, form):
        """
        Vérifie si le formulaire est valide.
        """
        print(f"Authentification réussie pour : {form.get_user()}")
        return super().form_valid(form)

    def get_success_url(self):
        """
        Renvoie l'URL de redirection.
        """
        next_url = self.request.POST.get("next") or self.request.GET.get("next")
        return next_url or reverse_lazy("home")


class DeconnexionView(LogoutView):
    """
    Vue pour la déconnexion.
    """
    next_page = "home"


@login_required(login_url="connexion")
def paiement_view(request):
    """
    Crée la vue pour le paiement.
    """
    utilisateur = request.user
    tickets = Ticket.objects.filter(utilisateur=utilisateur, est_achete=False)
    total = sum(ticket.get_prix_total() for ticket in tickets)

    if request.method == "POST":
        card_number = request.POST.get("cardNumber")
        expiry_date = request.POST.get("expiryDate")
        cvv = request.POST.get("cvv")

        if card_number and expiry_date and cvv:
            for ticket in tickets:
                for _ in range(ticket.quantite):
                    GenerationTicket.objects.create(ticket=ticket)
                ticket.est_achete = True
                ticket.save()

            messages.success(request, "Paiement réussi et billets générés !")

            return redirect("confirmation")
        else:
            messages.error(
                request, "Veuillez remplir tous les champs pour le paiement."
            )

    return render(request, "paiement.html", {"total": total})


@login_required(login_url="connexion")
def maj_quantite_view(request):
    """
    Met à jour la quantité d'un ticket dans le panier.
    """
    if request.method == "POST":
        ticket_id = request.POST.get("ticket_id")
        quantite = request.POST.get("quantite")

        try:
            ticket = Ticket.objects.get(
                id=ticket_id, utilisateur=request.user, est_achete=False
            )
            if quantite.isdigit() and int(quantite) > 0:
                ticket.quantite = int(quantite)
                ticket.save()
            else:
                return JsonResponse({"success": False, "message": "Quantité invalide."})
        except Ticket.DoesNotExist:
            return JsonResponse({"success": False, "message": "Ticket non trouvé."})

        tickets = Ticket.objects.filter(utilisateur=request.user, est_achete=False)
        total = sum(ticket.get_prix_total() for ticket in tickets)

        return JsonResponse({"success": True, "total": total})

    return JsonResponse({"success": False, "message": "Requête invalide."})


def confirmation_view(request):
    """
    Crée la vue pour la confirmation du paiement.
    """
    return render(
        request,
        "confirmation.html",
        {
            "message": "Votre paiement a bien été effectué et vos billets ont été générés !"
        },
    )


@login_required(login_url="connexion")
def mes_commandes_view(request):
    """
    Crée la vue pour les commandes de l'utilisateur.
    """
    utilisateur = request.user
    tickets = Ticket.objects.filter(utilisateur=utilisateur, est_achete=True)
    billets = GenerationTicket.objects.filter(ticket__utilisateur=utilisateur)

    return render(
        request, "mes_commandes.html", {"tickets": tickets, "billets": billets}
    )


@login_required(login_url="connexion")
def telecharger_billet_view(request, billet_id):
    """
    Télécharge un billet au format PDF.
    """
    billet = get_object_or_404(
        GenerationTicket, id=billet_id, ticket__utilisateur=request.user
    )
    nom_fichier = f"Billet_{billet.ticket.sport.nom}_{billet.ticket.utilisateur.prenom}_{billet.ticket.utilisateur.nom}.pdf"
    qr_code_url = billet.qr_code
    offre_formate = f"{billet.ticket.offre.type} - {locale.format_string('%.2f', billet.ticket.offre.prix, grouping=True)} €"
    html_string = render(
        request,
        "billet_pdf.html",
        {"billet": billet, "qr_code_url": qr_code_url, "offre_formate": offre_formate},
    ).content.decode("utf-8")
    html = HTML(string=html_string)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{nom_fichier}"'
    html.write_pdf(response)

    return response


# Vue ventes pour admin
@login_required(login_url="connexion")
def ventes_view(request):
    """
    Crée la vue pour les ventes.
    """
    billets = GenerationTicket.objects.all()

    total_billets = billets.count()

    total_billets_par_sport = GenerationTicket.objects.values(
        "ticket__sport__nom"
    ).annotate(
        total=Count("id"),
        total_prix=Sum(F("ticket__quantite") * F("ticket__offre__prix")),
    )

    total_billets_par_offre = GenerationTicket.objects.values(
        "ticket__offre__type"
    ).annotate(
        total=Count("id"),
        total_prix=Sum(F("ticket__quantite") * F("ticket__offre__prix")),
    )

    total_billets_par_sport_et_offre = GenerationTicket.objects.values(
        "ticket__sport__nom", "ticket__offre__type"
    ).annotate(
        total=Count("id"),
        total_prix=Sum(F("ticket__quantite") * F("ticket__offre__prix")),
    )

    total_prix_global = sum(item["total_prix"] for item in total_billets_par_offre)

    return render(
        request,
        "ventes.html",
        {
            "billets": billets,
            "total_billets": total_billets,
            "total_billets_par_sport": total_billets_par_sport,
            "total_billets_par_offre": total_billets_par_offre,
            "total_billets_par_sport_et_offre": total_billets_par_sport_et_offre,
            "total_prix_global": total_prix_global,
        },
    )
