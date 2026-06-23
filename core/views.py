from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from .models import Produtos,ProdutoCores,ProdutoImagens
import json
# Create your views here.

def home(request):
    if request.method == "GET":
        return render(request, 'index.html')

def products(request):
    if request.method == "GET":
        produtos = Produtos.objects.all()
        lista_produtos = [{
            "id" : p.id_produto,
            "codigo" : p.codigo,
            "descricao" : p.descricao,
            "valor" : p.valor,
            "quantidade" : float(p.quantidade),
            "altura": float(p.altura),
            "largura" : float(p.largura),
            "comprimento" : float(p.comprimento),
            "volume" : float(p.volume),
            "categoria" : p.categoria,
            "ativo" : p.ativo,
            "peso" : float(p.peso)
        }
            for p in produtos
        ]
        images = ProdutoImagens.objects.all()
        lista_images = [{
            "id_image" : i.id_imagem,
            "codigo" : i.codigo.codigo,
            "id_cor" : i.id_cor.id_cor,
            "imagem" : i.imagem.url,

        }
        for i in images
        ]
        return render(request, 'products.html', {
            'produtos_json' : json.dumps(lista_produtos),
            'images_json':json.dumps(lista_images)
        })
    
def detalhes(request, codigo):
    if request.method == "GET":
        produto = get_object_or_404(Produtos, codigo=codigo)
        cores = ProdutoCores.objects.filter(codigo=produto)
        images = ProdutoImagens.objects.filter(codigo=produto)
        lista_images = [{
            "id_image" : i.id_imagem,
            "id_cor" : i.id_cor.id_cor,
            "imagem" : i.imagem.url if i.imagem else "",

        }
        for i in images
        ]
        lista_cores = [{
            "id_cor" : c.id_cor,
            "cor":c.cor
        }
        for c in cores
        ]
        lista_produto = {
            "id" : produto.id_produto,
            "codigo" : produto.codigo,
            "descricao" : produto.descricao,
            "valor" : produto.valor,
            "quantidade" : float(produto.quantidade),
            "altura": float(produto.altura) if produto.altura else 0,
            "largura" : float(produto.largura) if produto.largura else 0,
            "comprimento" : float(produto.comprimento) if produto.comprimento else 0,
            "volume" : float(produto.volume) if produto.volume else 0,
            "categoria" : produto.categoria,
            "peso" : float(produto.peso) if produto.peso else 0
        }
        return render(request, 'detalhes.html', {
        'produto_json' : json.dumps(lista_produto),
        'cores_json':json.dumps(lista_cores),
        'images_json':json.dumps(lista_images)
        })
