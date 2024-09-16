from django.urls import path
from . import views
from django.conf import settings
from django.contrib.auth.views import LogoutView 
from django.conf.urls.static import static
from .views import ConnexionView, ticket_delete_view, telecharger_billet_view

urlpatterns = [
    path('', views.home, name='home'),
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', ConnexionView.as_view(), name='connexion'),  
    path('deconnexion/', LogoutView.as_view(next_page='home'), name='deconnexion'),  
    path('ticket/create/', views.ticket_create_view, name='ticket_create'),
    path('ticket/delete/<int:ticket_id>/', ticket_delete_view, name='ticket_delete'),
    path('tickets/', views.ticket_list_view, name='ticket_list'),
    path('ticket/<int:ticket_id>/update/', views.ticket_update_view, name='ticket_update'),
    path('ticket/<int:ticket_id>/delete/', views.ticket_delete_view, name='ticket_delete'),
    path('sport/', views.sport_list_view, name='sports_list'),
    path('get-sport-date/<int:sport_id>/', views.get_sport_date, name='get_sport_date'),
    path('panier/', views.panier_view, name='panier'),
    path('maj_quantite/', views.maj_quantite_view, name='maj_quantite'),
    path('paiement/', views.paiement_view, name='paiement'),
    path('confirmation/', views.confirmation_view, name='confirmation'),
    path('mes-commandes/', views.mes_commandes_view, name='mes_commandes'),
    path('telecharger-billet/<int:billet_id>/', telecharger_billet_view, name='telecharger_billet'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
