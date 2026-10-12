from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('produtos/', views.products,name="products"),
    path('produtos/<int:codigo>/',views.detalhes,name="detalhesProduto"),
    path("melhor-envio/autorizacao/",views.melhor_envio_autorizacao,name="melhor_envio_autorizacao"),
    path("api/melhorenvio/callback/",views.melhor_envio_callback,name="melhor_envio_callback"),
    path("calcular-frete-produto/",views.calcular_frete_produto,name="calcular_frete_produto"),
    path("pesquisar-produtos/",views.pesquisar_produtos,name="pesquisar_produtos"),
    
]