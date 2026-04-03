from django.contrib import admin
from django.urls import path
from core import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('reserva/nova/', views.nova_reserva, name='nova_reserva'),
    path('minhas-reservas/', views.minhas_reservas, name='minhas_reservas'),
    path('reserva/editar/<int:reserva_id>/', views.editar_reserva, name='editar_reserva'),
    path('reserva/deletar/<int:reserva_id>/', views.deletar_reserva, name='deletar_reserva'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
]