from django.shortcuts import render, get_object_or_404,redirect
from django.urls import reverse
from django.http import HttpResponse, Http404
from .models import Produtos,ProdutoCores,ProdutoImagens
import json
from django.db.models import Prefetch
from django.core.paginator import Paginator
from django.conf import settings
import requests
from datetime import timedelta
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from core.models import MelhorEnvioToken
from core.melhor_envio import MelhorEnvioAPI,obter_token_melhor_envio
from cart.cart import Cart
from urllib.parse import urlencode
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from playwright.sync_api import sync_playwright
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q, Case, When, IntegerField
from django_smart_ratelimit import ratelimit
# Create your views here.

def home(request):
    if request.method == "GET":
        return render(request, 'index.html')

@ratelimit(key="ip",rate="120/m",block=True,skip_if=lambda request: request.method != "GET")
def products(request):
    if request.method == "GET":
        busca = request.GET.get("busca", "").strip()
        produtos = Produtos.objects.filter(ativo=True).order_by("id_produto")
        if busca:
            produtos = produtos.filter(
                Q(descricao__icontains=busca) |
                Q(codigo__icontains=busca) |
                Q(categoria__icontains=busca)
            )
        imagens = ProdutoImagens.objects.all()
        produtos = produtos.prefetch_related(
            Prefetch(
                "produtoimagens_set",
                queryset=imagens,
                to_attr="imagens_produto"
            )
        )
        paginator = Paginator(produtos, 20)
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)
        for produto in page_obj:
            categorias = [
                categoria.strip()
                for categoria in produto.categoria.split(",")
                if categoria.strip()
            ]
            produto.nome_categoria = categorias[0] if categorias else ""
        return render(request, "products.html", {
            "produtos": page_obj,
            "busca": busca,
        })

@ratelimit(key="ip",rate="120/m",block=True,skip_if=lambda request: request.method != "GET")
def detalhes(request, codigo):
    if request.method == "GET":
        produto = get_object_or_404(Produtos, codigo=codigo)
        if produto.ativo == False:
            raise Http404()
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
            "cor": c.cor,
            "quantidade" : c.quantidade
        }
        for c in cores
        ]
        lista_produto = {
            "id" : produto.id_produto,
            "codigo" : produto.codigo,
            "descricao" : produto.descricao,
            "is_sale" : produto.is_sale,
            "sale_value" : float(produto.sale_value),
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

def melhor_envio_autorizacao(request):
    if not request.user.is_staff:
        raise Http404() 
    scopes = (
        "shipping-calculate "
        "ecommerce-shipping "
        "cart-read "
        "cart-write "
        "shipping-checkout "
        "shipping-generate "
        "shipping-print "
        "shipping-tracking "
        "shipping-cancel"
    )
    params = {
        "client_id": settings.MELHOR_ENVIO_CLIENT_ID,
        "redirect_uri": settings.MELHOR_ENVIO_REDIRECT_URI,
        "response_type": "code",
        "scope": scopes,
    }
    url = (
        f"{settings.MELHOR_ENVIO_BASE_URL}/oauth/authorize?"
        f"{urlencode(params)}"
    )
    return redirect(url)

def melhor_envio_callback(request):
    code = request.GET.get("code")
    if not code:
        return JsonResponse({
                "status": "erro",
                "mensagem": "Código de autorização não recebido."
            },status=400)
    response = requests.post(
        f"{settings.MELHOR_ENVIO_BASE_URL}/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id":settings.MELHOR_ENVIO_CLIENT_ID,
            "client_secret":settings.MELHOR_ENVIO_CLIENT_SECRET,
            "redirect_uri":settings.MELHOR_ENVIO_REDIRECT_URI,
            "code": code,
        },
        headers={
            "User-Agent":settings.MELHOR_ENVIO_USER_AGENT
        },
        timeout=30
    )
    if response.status_code != 200:
        return JsonResponse({
                "status": "erro",
                "mensagem": response.text
            },status=400)
    dados = response.json()
    access_token = dados.get("access_token")
    refresh_token = dados.get("refresh_token")
    expires_in = dados.get("expires_in")
    if not access_token or not refresh_token:
        return JsonResponse({
                "status": "erro",
                "mensagem": "Token não retornado pelo Melhor Envio."
            },status=400)
    MelhorEnvioToken.objects.all().delete()
    MelhorEnvioToken.objects.create(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=timezone.now()+ timedelta(seconds=expires_in)
    )
    return redirect("homePerfil")

@ratelimit(key="ip",rate="60/m",block=True,skip_if=lambda request: request.method != "POST")
def calcular_frete_produto(request):
    if request.method != "POST":
        raise Http404()
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
                "status": "erro",
                "mensagem": "Corpo da requisição inválido"
            },status=400)
    produto_id = data.get("produto_id")
    cep = data.get("cep")
    if not produto_id or not cep:
        return JsonResponse({
                "status": "erro",
                "mensagem":"Produto e CEP são obrigatórios."
            },status=400)
    try:
        produto = Produtos.objects.get(id_produto=produto_id)
    except Produtos.DoesNotExist:
        return JsonResponse({
                "status": "erro",
                "mensagem": "Produto não encontrado."
            },status=400)
    access_token = obter_token_melhor_envio()
    if not access_token:
        return JsonResponse({
                "status": "erro",
                "mensagem":"Melhor Envio não está conectado."
            },status=400)
    valor = 0
    if produto.is_sale == True:
        valor = produto.sale_value
    else:
        valor = produto.valor
    produto_api = {
        "id":str(produto.id_produto),
        "width":float(produto.largura),
        "height":float(produto.altura),
        "length":float(produto.comprimento),
        "weight":float(produto.peso),
        "insurance_value":float(valor),
        "quantity":1
    }
    api = MelhorEnvioAPI(access_token=access_token)
    response = api.calcular_frete(
        cep_origem=settings.MELHOR_ENVIO_FROM_POSTAL_CODE,
        cep_destino=cep,
        produtos=[produto_api] 
    )
    if response.status_code != 200:
        return JsonResponse({
                "status": "erro",
                "mensagem":"Erro ao consultar Melhor Envio.",
                "detalhes":response.json()
            },status=response.status_code)
    opcoes = response.json()
    return JsonResponse({
            "status": "ok",
            "opcoes": opcoes,
            "mensagem": "Opções de frete renderizadas."
        }
    )

@ratelimit(key="ip",rate="120/m",block=True,skip_if=lambda request: request.method != "GET")
def pesquisar_produtos(request):
    busca = request.GET.get("q", "").strip()

    if not busca:
        return JsonResponse({
            "status": "ok",
            "produtos": []
        })
    produtos = Produtos.objects.filter(
        ativo=True
    ).filter(
        Q(descricao__icontains=busca) |
        Q(codigo__icontains=busca) |
        Q(categoria__icontains=busca)
    ).annotate(
        relevancia=Case(
            When(descricao__iexact=busca, then=3),
            When(descricao__istartswith=busca, then=2),
            When(codigo__iexact=busca, then=2),
            default=1,
            output_field=IntegerField()
        )
    ).order_by(
        "-relevancia",
        "descricao"
    )[:6]
    resultado = []
    for produto in produtos:
        imagem = ProdutoImagens.objects.filter(codigo=produto).first()
        is_sale = getattr(produto, "is_sale", False)
        if is_sale:
            preco_final = str(produto.sale_value)    
            preco_antigo = str(produto.valor)        
        else:
            preco_final = str(produto.valor)       
            preco_antigo = None
        resultado.append({
            "id": produto.id_produto,
            "codigo": produto.codigo,
            "nome": produto.categoria.split(",")[0],
            "preco": preco_final,
            "preco_antigo": preco_antigo,
            "imagem": imagem.imagem.url if imagem and imagem.imagem else None,
            "is_sale": getattr(produto, "is_sale", False),
        })
    return JsonResponse({
        "status": "ok",
        "produtos": resultado
    })