from django.db import models
from django.contrib.auth.models import User

class Sala(models.Model):
    nome = models.CharField(max_length=50)
    capacidade = models.IntegerField()

    def __str__(self):
        return self.nome

class Item(models.Model):
    nome = models.CharField(max_length=50)

    def __str__(self):
        return self.nome

class Reserva(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    itens = models.ManyToManyField(Item, blank=True)
    data = models.DateField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    nome_evento = models.CharField(max_length=200)
    def __str__(self):
        return f"{self.sala.nome} - {self.usuario.username} ({self.data})"
