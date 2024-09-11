from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('inscription/', views.inscription, name='inscription'),
    path('ticket/create/', views.ticket_create_view, name='ticket_create'),
    path('tickets/', views.ticket_list_view, name='ticket_list'),
    path('sport/', views.sport_list_view, name='ticket_sport'),
    path('ticket/<int:ticket_id>/update/', views.ticket_update_view, name='ticket_update'),
    path('ticket/<int:ticket_id>/delete/', views.ticket_delete_view, name='ticket_delete'),
]
