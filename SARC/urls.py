from django.urls import path, re_path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("reservas/", views.reserva, name="reservas"),
    path("salas/", views.salas, name="salas"),
    path("cadastro/", views.cadastro, name="cadastro"),
    re_path(r'^reservar-sala(?:/(?P<id_sala>\d+)/)?$', views.reservar_sala, name='reservar_sala'),
    path("login/", views.login, name="login"),
    path("editar_reserva/<int:id_reserva>/", views.editar_reserva, name="editar_reserva"),
    path("cancelar_reserva/<int:id_reserva>/", views.cancelar_reserva, name="cancelar_reserva"),
    path("marcar_presenca/<int:id_reserva>/", views.marcar_presenca, name="marcar_presenca"),  # nova rota
    path("dashboard/", views.dashboard_bolsista, name="dashboard_bolsista"),
]
