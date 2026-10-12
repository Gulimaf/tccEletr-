import json
from datetime import timedelta
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from core.models import CotacaoFrete, OpcaoFrete, MelhorEnvioToken
from core.melhor_envio import obter_token_melhor_envio
from cart.cart import Cart
from melhor_envio.services import calcular_frete
from django_smart_ratelimit import ratelimit

@ratelimit(key="ip",rate="60/m",block=True,skip_if=lambda request: request.method != "POST")
def cotar_carrinho(request):
    if request.method != "POST":
        return JsonResponse({
            "status": "erro",
            "mensagem": "Método não permitido."
        }, status=405)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            "status": "erro",
            "mensagem": "Corpo da requisição inválido"
        }, status=400)
    cep = data.get("cep", "")
    cep = "".join(c for c in cep if c.isdigit())
    if len(cep) != 8:
        return JsonResponse({
            "status": "erro",
            "mensagem": "CEP inválido."
        }, status=400)
    cart = Cart(request)
    if not cart.cart:
        return JsonResponse({
            "status": "erro",
            "mensagem": "Carrinho vazio."
        }, status=400)
    produtos = cart.get_produtos_frete()
    if not produtos:
        return JsonResponse({   
                "status": "erro",
                "mensagem": "Não foi possível obter os produtos."}, status=400)
    carrinho_hash = cart.get_cart_hash()
    cep_origem = '13733446'
    access_token = obter_token_melhor_envio()
    response = calcular_frete(token=access_token,cep_origem=cep_origem,cep_destino=cep,produtos=produtos)
    if response.status_code != 200:
        return JsonResponse({
            "status": "erro",
            "mensagem": "Não foi possível calcular o frete."}, status=400)
    resposta = response.json()
    cotacao = CotacaoFrete.objects.create(
        usuario=(request.user if request.user.is_authenticated else None),
        cep_origem=cep_origem,
        cep_destino=cep,
        carrinho_hash=carrinho_hash,
        resposta_api=resposta,
        expira_em=(timezone.now()+ timedelta(minutes=30))
    )
    opcoes = []
    for opcao in resposta:
        if opcao.get("error"):
            continue
        preco = opcao.get("custom_price")
        if preco is None:
            preco = opcao.get("price")
        if preco is None:
            continue
        try:
            company = opcao.get("company",{})
            opcao_db = OpcaoFrete.objects.create(
                cotacao=cotacao,
                service_id=opcao["id"],
                transportadora_id=company.get("id"),
                transportadora_nome=company.get("name","Transportadora"),
                nome=opcao.get("name","Serviço"),
                preco=preco,
                prazo=opcao.get("custom_delivery_time"),
                resposta_api=opcao
            )
            opcoes.append({
                "id": opcao_db.id,
                "transportadora": (opcao_db.transportadora_nome),
                "servico": (opcao_db.nome),
                "preco": str(opcao_db.preco),
                "prazo": (opcao_db.prazo),
                "logo": opcao["company"]["picture"],
            })
        except Exception as e:
            return JsonResponse({
                "status" : "erro",
                "mensagem" : str(e)
            })
        
    return JsonResponse({
        "status": "ok",
        "mensagem" : "Opções de frete renderizadas.",
        "cotacao_id": cotacao.id,
        "opcoes": opcoes,
        "r" : resposta
        
    })

@ratelimit(key="user",rate="30/m",block=True,skip_if=lambda request: request.method != "POST")
def selecionar_frete(request):
    if request.method != "POST":
        return JsonResponse({
            "status": "erro"
        }, status=405)
    data = json.loads(request.body)
    cotacao_id = data.get("cotacao_id")
    opcao_id = data.get("opcao_id")
    try:
        cotacao = CotacaoFrete.objects.get(
            id=cotacao_id,
            ativa=True
        )
        opcao = OpcaoFrete.objects.get(
            id=opcao_id,
            cotacao=cotacao
        )
    except (CotacaoFrete.DoesNotExist,OpcaoFrete.DoesNotExist):
        return JsonResponse({
            "status": "erro",
            "mensagem":"Frete inválido."
        }, status=400)
    if cotacao.expira_em < timezone.now():
        return JsonResponse({
            "status": "erro",
            "mensagem":"A cotação expirou."
        }, status=400)
    cart = Cart(request)
    if (cart.get_cart_hash()!= cotacao.carrinho_hash):
        return JsonResponse({
            "status": "erro",
            "mensagem":"O carrinho foi alterado. Calcule o frete novamente."
        }, status=400)

    request.session["frete_selecionado"] = {
        "cotacao_id":cotacao.id,
        "opcao_id":opcao.id
    }
    request.session.modified = True
    return JsonResponse({
        "status": "ok",
        "preco":str(opcao.preco),
        "prazo":opcao.prazo,
        "transportadora":opcao.transportadora_nome,
        "mensagem" : "Frete selecionado."
    })