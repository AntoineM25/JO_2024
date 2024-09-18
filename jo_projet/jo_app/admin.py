# Models dans l'admin
from django.contrib import admin
from .models import Utilisateur, Sport, Offre, Ticket, Paiement, GenerationTicket

admin.site.register(Utilisateur)
admin.site.register(Sport)
admin.site.register(Offre)
admin.site.register(Ticket)
admin.site.register(Paiement)
admin.site.register(GenerationTicket)
