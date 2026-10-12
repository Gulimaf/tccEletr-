from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("cotar-frete-carrinho/",views.cotar_carrinho,name="cotar_carrinho"),
    path("selecionar-frete/",views.selecionar_frete,name="cotar_carrinho"),
]