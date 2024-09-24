"""
Ce module gère l'administration de l'application via Django Admin.
"""

from django.contrib import admin

from .models import GenerationTicket, Offre, Paiement, Sport, Ticket, Utilisateur

admin.site.register(Utilisateur)
admin.site.register(Sport)
admin.site.register(Offre)
admin.site.register(Ticket)
admin.site.register(Paiement)
admin.site.register(GenerationTicket)
