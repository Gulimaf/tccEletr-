from django.db import models

# Create your models here.
class ProdutoCores(models.Model):
    id_cor = models.AutoField(primary_key=True)
    codigo = models.ForeignKey('Produtos', models.DO_NOTHING, db_column='codigo', blank=True, null=True)
    cor = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'produto_cores'


class ProdutoImagens(models.Model):
    id_imagem = models.AutoField(primary_key=True)
    codigo = models.ForeignKey('Produtos', models.DO_NOTHING, db_column='codigo', blank=True, null=True)
    id_cor = models.ForeignKey('ProdutoCores', models.DO_NOTHING, db_column='id_cor', blank=True, null=True)
    imagem = models.ImageField(upload_to='produtos/',blank=True,null=True)

    class Meta:
        managed = True
        db_table = 'produto_imagens'


class Produtos(models.Model):
    id_produto = models.AutoField(primary_key=True)
    descricao = models.CharField(max_length=500, blank=True, null=True)
    valor = models.FloatField(blank=True, null=True)
    quantidade = models.IntegerField(blank=True, null=True)
    categoria = models.TextField(blank=True, null=True)
    ativo = models.IntegerField(blank=True, null=True)
    codigo = models.IntegerField(blank=False, null=False)
    altura = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    largura = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    comprimento = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    peso = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    volume = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    class Meta:
        managed = True
        db_table = 'produtos'
