from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginF, name="login"),
    path('cadastro/', views.register, name="register"),
    path('confirmar-email/<int:user_id>/<str:token>/', views.confirmarEmail, name='confirmar-email'),
    path('reenviar-confirmacao/', views.reenviarConfirmacao, name="reenviar-confirmacao"),
    path('perfil/',views.loadPerfil, name='homePerfil'),
    path('logout/',views.logoutF, name="logout"),
    path('redefinir-senha-p1/',views.redefinirSenha,name="redefinirSenha"),
    path('redefinir-senha-p2/<int:user_id>/<str:token>/',views.resetPassword,name="redefinirSenhap2"),
    path('cadastrar-produto/',views.cadProduto,name='cadProduto'),
    path('cadastrar-produto/<int:id_produto>/',views.cadProduto,name='cadProdutoDetalhe'),
    path('cadastrar-cor/',views.cadastrar_cor,name="cadCor"),
    path('cadastrar-imagem/',views.cadastrar_imagem,name="cadImagem"),
]