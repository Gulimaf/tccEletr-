from django.db import models
from django.contrib.auth.models import User
from core.models import Produtos, ProdutoCores

class Pedido(models.Model):
    STATUS_CHOICES = [
        ("aguardando_pagamento", "Aguardando pagamento"),
        ("pago", "Pago"),
        ("preparando", "Preparando pedido"),
        ("pronto_retirada", "Pronto para retirada"),
        ("etiqueta_gerada", "Etiqueta gerada"),
        ("enviado", "Enviado"),
        ("entregue", "Entregue"),
        ("cancelado", "Cancelado"),
    ]
    METODOS_ENTREGA = [
        ("frete", "Entrega"),
        ("retirada", "Retirada na loja"),
    ]
    metodo_entrega = models.CharField(max_length=20, choices=METODOS_ENTREGA, default="frete")
    usuario = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name="pedidos")
    nome_cliente = models.CharField(max_length=150)
    email_cliente = models.EmailField()
    telefone_cliente = models.CharField(max_length=30,blank=True)
    status = models.CharField(max_length=30,choices=STATUS_CHOICES,default="aguardando_pagamento")
    subtotal = models.DecimalField(max_digits=10,decimal_places=2)
    frete = models.DecimalField(max_digits=10,decimal_places=2)
    total = models.DecimalField(max_digits=10,decimal_places=2)
    cep = models.CharField(max_length=8, blank=True,null=True)
    endereco = models.CharField(max_length=255, blank=True,null=True)
    numero = models.CharField(max_length=20, blank=True,null=True)
    complemento = models.CharField(max_length=100,blank=True,null=True)
    bairro = models.CharField(max_length=100, blank=True,null=True)
    cidade = models.CharField(max_length=100, blank=True,null=True)
    estado = models.CharField(max_length=2, blank=True,null=True)
    transportadora = models.CharField(max_length=100, blank=True,null=True)
    servico_frete = models.CharField(max_length=150, blank=True,null=True)
    prazo_frete = models.PositiveIntegerField(null=True,blank=True)
    cotacao_frete_id = models.PositiveIntegerField(null=True,blank=True)
    opcao_frete_id = models.PositiveIntegerField(null=True,blank=True)
    melhor_envio_shipment_id = models.CharField(max_length=100,null=True,blank=True)
    melhor_envio_order_id = models.CharField(max_length=100,null=True,blank=True)
    codigo_rastreio = models.CharField(max_length=100,null=True,blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    mp_preference_id = models.CharField(max_length=150,null=True,blank=True, unique=True)
    mp_payment_id = models.CharField(max_length=150,null=True, blank=True)
    mp_status = models.CharField(max_length=50,null=True,blank=True)
    mp_status_detail = models.CharField(max_length=100,null=True,blank=True)
    data_pagamento = models.DateTimeField(null=True,blank=True)
    processamento_pos_pagamento = models.BooleanField(default=False)
    etiqueta_url = models.URLField(blank=True,null=True)
    etiqueta_paga = models.BooleanField(default=False)
    def __str__(self):
        return f"Pedido #{self.id}"

class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido,on_delete=models.CASCADE,related_name="itens")
    produto = models.ForeignKey(Produtos,on_delete=models.PROTECT)
    cor = models.ForeignKey(ProdutoCores,on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10,decimal_places=2)
    subtotal = models.DecimalField(max_digits=10,decimal_places=2)
    def __str__(self):return f"{self.produto} - {self.quantidade}"