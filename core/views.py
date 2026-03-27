from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from .models import Sala, Item, Reserva

# Página inicial
@login_required
def home(request):
    salas = Sala.objects.all()
    agora = timezone.localtime()  # horário do Brasil, datetime aware

    salas_status = []
    for sala in salas:
        reserva_atual = None

        # Pega todas reservas do dia
        reservas_do_dia = Reserva.objects.filter(
            sala=sala,
            data=agora.date()
        ).order_by('hora_inicio')

        # Verifica se a sala está ocupada agora
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

# Nova reserva
@login_required
def nova_reserva(request):
    salas = Sala.objects.all()
    itens = Item.objects.all()

    if request.method == "POST":
        sala_id = request.POST.get('sala')
        data = request.POST.get('data')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fim = request.POST.get('hora_fim')
        itens_selecionados = request.POST.getlist('itens')

        sala = Sala.objects.get(id=sala_id)

        # Verifica se a sala já está ocupada no horário escolhido
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
                hora_fim=hora_fim
            )
            reserva.itens.set(itens_selecionados)
            reserva.save()
            messages.success(request, "Reserva criada com sucesso!")
            return redirect('home')

    return render(request, 'nova_reserva.html', {'salas': salas, 'itens': itens})

# Minhas reservas
@login_required
def minhas_reservas(request):
    reservas = Reserva.objects.filter(usuario=request.user).order_by('data', 'hora_inicio')
    return render(request, 'minhas_reservas.html', {'reservas': reservas})

@login_required
def editar_reserva(request, reserva_id):
    reserva = Reserva.objects.get(id=reserva_id, usuario=request.user)
    salas = Sala.objects.all()
    itens = Item.objects.all()

    if request.method == "POST":
        reserva.sala_id = request.POST.get('sala')
        reserva.data = request.POST.get('data')
        reserva.hora_inicio = request.POST.get('hora_inicio')
        reserva.hora_fim = request.POST.get('hora_fim')
        itens_selecionados = request.POST.getlist('itens')
        reserva.itens.set(itens_selecionados)
        reserva.save()
        messages.success(request, "Reserva atualizada!")
        return redirect('minhas_reservas')

    return render(request, 'editar_reserva.html', {'reserva': reserva, 'salas': salas, 'itens': itens})

@login_required
def deletar_reserva(request, reserva_id):
    reserva = Reserva.objects.get(id=reserva_id, usuario=request.user)
    reserva.delete()
    messages.success(request, "Reserva excluída!")
    return redirect('minhas_reservas')