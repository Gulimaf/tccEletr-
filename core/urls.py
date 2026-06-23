from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('produtos/', views.products,name="products"),
    path('produtos/<int:codigo>/',views.detalhes,name="detalhesProduto"),
]