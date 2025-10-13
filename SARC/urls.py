from django.urls import path
from . import views
urlpatterns = [
    path("", views.index, name="index"),
    path("aluno",views.home_alu, name="home_alu"),
    path("professor",views.home_pro, name="home_pro"),
    path("bolsista",views.home_bol, name="home_bol"),
    path("reservas/", views.reserva, name="reservas"),
    path("salas/", views.salas, name="salas"),
    path("cadastro/", views.cadastro, name="cadastro"),
    path("reservar sala/", views.reservar_sala, name="reservar_sala"),
    path("login/", views.login, name="login"),
]
