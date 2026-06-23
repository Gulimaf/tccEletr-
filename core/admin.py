from django.contrib import admin
from .models import ProdutoCores, Produtos, ProdutoImagens

admin.site.register(Produtos)
admin.site.register(ProdutoImagens)
admin.site.register(ProdutoCores)
# Register your models here.
