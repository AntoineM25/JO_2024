from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView  

urlpatterns = [
    path('', views.home, name='home'),
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', LoginView.as_view(template_name='connexion.html'), name='connexion'),  
    path('deconnexion/', LogoutView.as_view(next_page='home'), name='deconnexion'),  
    path('ticket/create/', views.ticket_create_view, name='ticket_create'),
    path('tickets/', views.ticket_list_view, name='ticket_list'),
    path('ticket/<int:ticket_id>/update/', views.ticket_update_view, name='ticket_update'),
    path('ticket/<int:ticket_id>/delete/', views.ticket_delete_view, name='ticket_delete'),
    path('sport/', views.sport_list_view, name='sports_list'),
    path('get-sport-date/<int:sport_id>/', views.get_sport_date, name='get_sport_date'),
    path('panier/', views.panier_view, name='panier'),
]
