from django.contrib import admin
from .models import ProdutoCores, Produtos, ProdutoImagens, CotacaoFrete, MelhorEnvioToken, OpcaoFrete

admin.site.register(Produtos)
admin.site.register(ProdutoImagens)
admin.site.register(ProdutoCores)
admin.site.register(CotacaoFrete)
admin.site.register(MelhorEnvioToken)
admin.site.register(OpcaoFrete)
# Register your models here.
