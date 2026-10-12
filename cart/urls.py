from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('carrinho/', views.cart, name="cart"),
    path("selecionar-metodo-entrega/",views.selecionar_metodo_entrega,name="selecionar_metodo_entrega"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
