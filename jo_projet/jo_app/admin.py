# Models dans l'admin
from django.contrib import admin
from .models import Utilisateur, Ticket, Paiement, GenerationTicket

admin.site.register(Utilisateur)
admin.site.register(Ticket)
admin.site.register(Paiement)
admin.site.register(GenerationTicket)