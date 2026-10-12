from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
import uuid
# Create your models here.
class ProdutoCores(models.Model):
    id_cor = models.AutoField(primary_key=True)
    codigo = models.ForeignKey('Produtos', on_delete=models.CASCADE, db_column='codigo', blank=True, null=True,related_name="cores")
    cor = models.CharField(max_length=20, blank=True, null=True)
    quantidade = models.PositiveIntegerField(default=0)
    nome = models.TextField(blank=True, null=True)
    ativo = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = True
        db_table = 'produto_cores'


class ProdutoImagens(models.Model):
    id_imagem = models.AutoField(primary_key=True)
    codigo = models.ForeignKey('Produtos', on_delete=models.CASCADE, db_column='codigo', blank=True, null=True,)
    id_cor = models.ForeignKey('ProdutoCores', on_delete=models.CASCADE, db_column='id_cor', blank=True, null=True)
    imagem = models.ImageField(upload_to='produtos/',blank=True,null=True)
    ativo = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = True
        db_table = 'produto_imagens'


class Produtos(models.Model):
    id_produto = models.AutoField(primary_key=True)
    descricao = models.CharField(max_length=500, blank=True, null=True)
    valor = models.FloatField(blank=True, null=True)
    # quantidade = models.IntegerField(blank=True, null=True)
    categoria = models.TextField(blank=True, null=True)
    ativo = models.IntegerField(blank=True, null=True)
    codigo = models.IntegerField(blank=False, null=False)
    altura = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    largura = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    comprimento = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    peso = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    volume = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_sale = models.BooleanField(default=False)
    sale_value = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    @property
    def quantidade(self):
        return self.cores.aggregate(
            total=Sum("quantidade")
        )["total"] or 0
    class Meta:
        managed = True
        db_table = 'produtos'

class MelhorEnvioToken(models.Model):
    access_token = models.TextField()
    refresh_token = models.TextField()
    expires_at = models.DateTimeField()
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    def __str__(self):
        return "Token Melhor Envio"



class CotacaoFrete(models.Model):
    usuario = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    cep_origem = models.CharField(max_length=8)
    cep_destino = models.CharField(max_length=8)
    carrinho_hash = models.CharField(max_length=64,default=uuid.uuid4)
    resposta_api = models.JSONField()
    criada_em = models.DateTimeField(auto_now_add=True)
    expira_em = models.DateTimeField()
    ativa = models.BooleanField(default=True)
    def __str__(self):
        return f"Cotação {self.id} - {self.cep_destino}"

class OpcaoFrete(models.Model):
    cotacao = models.ForeignKey(CotacaoFrete,on_delete=models.CASCADE,related_name="opcoes")
    service_id = models.IntegerField()
    transportadora_id = models.IntegerField(null=True,blank=True)
    transportadora_nome = models.CharField(max_length=100)
    nome = models.CharField(max_length=150)
    preco = models.DecimalField(max_digits=10,decimal_places=2)
    prazo = models.IntegerField(null=True,blank=True)
    resposta_api = models.JSONField()
    selecionada = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.transportadora_nome} - {self.preco}"