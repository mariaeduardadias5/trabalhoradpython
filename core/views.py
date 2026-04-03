from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from .models import Sala, Item, Reserva
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User


@login_required
def home(request):
    salas = Sala.objects.all()
    agora = timezone.localtime()  

    salas_status = []
    for sala in salas:
        reserva_atual = None

       
        reservas_do_dia = Reserva.objects.filter(
            sala=sala,
            data=agora.date()
        ).order_by('hora_inicio')

        
        for r in reservas_do_dia:
            inicio = timezone.make_aware(datetime.combine(r.data, r.hora_inicio))
            fim = timezone.make_aware(datetime.combine(r.data, r.hora_fim))

            if inicio <= agora <= fim:
                reserva_atual = r
                break

        salas_status.append({
            'sala': sala,
            'ocupada': reserva_atual is not None,
            'reserva_atual': reserva_atual,
            'reservas': reservas_do_dia
        })

    return render(request, 'home.html', {'salas_status': salas_status})


@login_required
def nova_reserva(request):
    salas = Sala.objects.all()
    itens = Item.objects.all()

    if request.method == "POST":
        nome_evento = request.POST.get('nome_evento')
        sala_id = request.POST.get('sala')
        data = request.POST.get('data')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fim = request.POST.get('hora_fim')
        itens_selecionados = request.POST.getlist('itens')


        sala = Sala.objects.get(id=sala_id)

        reservas_existentes = Reserva.objects.filter(
            sala=sala,
            data=data,
            hora_inicio__lt=hora_fim,
            hora_fim__gt=hora_inicio
        )

        if reservas_existentes.exists():
            messages.error(request, "Sala ocupada neste horário!")
        else:
            
            reserva = Reserva.objects.create(
                usuario=request.user,
                sala=sala,
                data=data,
                hora_inicio=hora_inicio,
                hora_fim=hora_fim,
                nome_evento=nome_evento
            )
            
            reserva.itens.set(itens_selecionados)
            reserva.save()
            return redirect('home')

    
    return render(request, 'nova_reserva.html', {'salas': salas, 'itens': itens})



@login_required
def minhas_reservas(request):
    reservas = Reserva.objects.filter(usuario=request.user).order_by('data', 'hora_inicio')
    return render(request, 'minhas_reservas.html', {'reservas': reservas})

@login_required
def editar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)
    salas = Sala.objects.all()
    itens = Item.objects.all()

    if request.method == "POST":
        # Pegando dados do formulário
        nome_evento = request.POST.get('nome_evento')
        sala_id = request.POST.get('sala')
        data = request.POST.get('data')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fim = request.POST.get('hora_fim')
        itens_selecionados = request.POST.getlist('itens')

        sala = Sala.objects.get(id=sala_id)

    
        conflito = Reserva.objects.filter(
            sala=sala,
            data=data,
            hora_inicio__lt=hora_fim,
            hora_fim__gt=hora_inicio
        ).exclude(id=reserva.id)

        if conflito.exists():
            messages.error(request, "Já existe uma reserva nesse horário!")
        else:
            # Atualizando os dados
            reserva.nome_evento = nome_evento
            reserva.sala = sala
            reserva.data = data
            reserva.hora_inicio = hora_inicio
            reserva.hora_fim = hora_fim

            reserva.save()
            reserva.itens.set(itens_selecionados)

            return redirect('minhas_reservas')

    return render(request, 'editar_reserva.html', {
        'reserva': reserva,
        'salas': salas,
        'itens': itens
    })

@login_required
def deletar_reserva(request, reserva_id):
    reserva = Reserva.objects.get(id=reserva_id, usuario=request.user)
    reserva.delete()
    return redirect('minhas_reservas')

def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        senha = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
            user = authenticate(username=user.username, password=senha)

            if user is not None:
                auth_login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Senha incorreta.")

        except User.DoesNotExist:
            messages.error(request, "Email não encontrado.")

        return render(request, 'login.html')