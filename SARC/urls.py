from django.urls import path, re_path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("", views.index, name="index"),
    path("reservas/", views.reserva, name="reservas"),
    path("salas/", views.salas, name="salas"),
    path("cadastro/", views.cadastro, name="cadastro"),
    re_path(r'^reservar-sala(?:/(?P<id_sala>\d+)/)?$', views.reservar_sala, name='reservar_sala'),
    path("login/", views.login, name="login"),
    path("editar_reserva/<int:id_reserva>/", views.editar_reserva, name="editar_reserva"),
    path("cancelar_reserva/<int:id_reserva>/", views.cancelar_reserva, name="cancelar_reserva"),
    path("marcar_presenca/<int:id_reserva>/", views.marcar_presenca, name="marcar_presenca"),
    path("dashboard/", views.dashboard_bolsista, name="dashboard_bolsista"),
    # ajax endpoints
    path("api/check_availability/", views.check_availability, name="check_availability"),
    path("api/bloquear_sala/", views.bloquear_sala, name="bloquear_sala"),
    path("api/desbloquear_sala/", views.desbloquear_sala, name="desbloquear_sala"),
    path("api/editar_reserva/", views.editar_reserva_ajax, name="editar_reserva_ajax"),
    path("api/cancelar_reserva/", views.cancelar_reserva_ajax, name="cancelar_reserva_ajax"),
    path('bolsista/criar_sala/', views.criar_sala, name='criar_sala'),
    path('bolsista/criar_computador/', views.criar_computador, name='criar_computador'),
    path('salas/<int:sala_id>/editar/', views.editar_sala, name='editar_sala'),

    # rota de logout (view padrão do Django)
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
    path('computador/remover/<int:computador_id>/', views.remover_computador, name='remover_computador'),
]
