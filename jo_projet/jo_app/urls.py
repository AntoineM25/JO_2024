from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('inscription/', views.inscription, name='inscription'),
    path('ticket/create', views.ticket, name='ticket_create'),
    path('ticket/<int:ticket_id>/update/', views.ticket_update_view, name='ticket_update'),
    path('ticket/<int:ticket_id>/delete/', views.ticket_delete_view, name='ticket_delete'),
]
