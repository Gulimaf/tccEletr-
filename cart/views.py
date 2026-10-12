from django.shortcuts import render
from .cart import Cart
from core.models import Produtos, OpcaoFrete
from django.http import JsonResponse, Http404
import json
from django.utils import timezone
from django_smart_ratelimit import ratelimit


def cart(request):
    cart = Cart(request)
    if request.method == "GET":
        if "frete_selecionado" in request.session:
            del request.session["frete_selecionado"]
            request.session.modified = True
        cart_produtos = cart.get_produtos()
        cart_subtotal = sum(
            item["subtotal"]
            for item in cart_produtos
        )
        frete_selecionado = request.session.get("frete_selecionado")
        shipping_cost = None
        erro = request.session.pop("erro", None)
        if frete_selecionado:
            try:
                opcao = OpcaoFrete.objects.get(
                    id=frete_selecionado["opcao_id"],
                    cotacao__id=frete_selecionado["cotacao_id"],
                    cotacao__ativa=True
                )
                if opcao.cotacao.expira_em >= timezone.now():
                    if (cart.get_cart_hash()== opcao.cotacao.carrinho_hash):
                        shipping_cost = opcao.preco
                    else:
                        request.session.pop("frete_selecionado",None)
            except OpcaoFrete.DoesNotExist:
                request.session.pop("frete_selecionado",None)
        cart_total = cart_subtotal
        if shipping_cost is not None:
            cart_total += float(shipping_cost)
        return render(request,'carrinho.html',{
                'cart_items': cart_produtos,
                'cart_subtotal': cart_subtotal,
                'shipping_cost': shipping_cost,
                'cart_total': cart_total,
                'erro': erro
            }
        )
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse({
                'status' : 'Erro', 
                'mensagem':'Corpo da requisição inválido'},status=400)
        produto_id = data.get('produto_id')
        color_id = data.get('cor_id') 
        quantity = data.get('quantity', 1)
        if not produto_id or not color_id: 
            return JsonResponse({ 
                'status': 'erro', 
                'mensagem': 'Produto e cor são obrigatórios.' }, status=400)
        try: 
            produto = Produtos.objects.get( id_produto=produto_id )
        except Produtos.DoesNotExist: 
            return JsonResponse({ 
                'status': 'erro',
                'mensagem': 'Produto não encontrado.' }, status=404)
        try:
            sucesso, mensagem = cart.add(produto=produto, id_cor=color_id, quantidade=quantity)
            if not sucesso: 
                return JsonResponse({ 
                    'status': 'erro', 
                    'mensagem': mensagem }, status=400)
        except Exception as e:
            return JsonResponse({
                'status' : 'erro',
                'mensagem': 'Erro ao adicionar no carrinho.'
            },status=422)
        cart_quantity = len(cart)
        return JsonResponse({ 
            'status': 'ok', 
            'mensagem': mensagem, 
            'cart_quantity': cart_quantity })
    if request.method == "PUT": 
        try: 
            data = json.loads(request.body) 
        except json.JSONDecodeError: 
            return JsonResponse({ 
                'status': 'erro', 
                'mensagem': 'Corpo da requisição inválido.' }, status=400) 
        produto_id = data.get('produto_id') 
        color_id = data.get('cor_id') 
        quantity = data.get('quantidade') 
        if not produto_id or not color_id or quantity is None: 
            return JsonResponse({ 
                'status': 'erro', 
                'mensagem': 'Produto, cor e quantidade são obrigatórios.' }, status=400) 
        sucesso, resultado = cart.update_quantity( produto_id=produto_id, id_cor=color_id, quantidade=quantity ) 
        if not sucesso: 
            return JsonResponse({ 
                'status': 'erro', 
                'mensagem': resultado }, status=400) 
        request.session.pop("frete_selecionado",None)
        request.session.modified = True
        return JsonResponse({ 
            'status': 'ok', 
            'quantity': resultado, 
            'cart_quantity': len(cart) })
    if request.method == "DELETE": 
        try: 
            data = json.loads(request.body) 
        except json.JSONDecodeError: 
            return JsonResponse({ 
                'status': 'erro', 
                'mensagem': 'Corpo da requisição inválida.' }, status=400) 
        produto_id = data.get('produto_id') 
        color_id = data.get('cor_id') 
        if not produto_id or not color_id: 
            return JsonResponse({ 
                'status': 'erro', 
                'mensagem': 'Produto e cor são obrigatórios.' }, status=400) 
        removido = cart.remove( produto_id=produto_id, id_cor=color_id) 
        request.session.pop("frete_selecionado",None)
        request.session.modified = True
        if not removido: 
            return JsonResponse({ 
                'status': 'erro', 
                'mensagem': 'Item não encontrado no carrinho.' }, status=404) 
        return JsonResponse({ 
            'status': 'ok', 
            'cart_quantity': len(cart),
            'mensagem': 'Produto excluído do carrinho.', })
    raise Http404()

def selecionar_metodo_entrega(request):
    if request.method != "POST":
        return JsonResponse({
            "status": "erro",
            "mensagem": "Método não permitido."
        }, status=405)
    try:
        data = json.loads(request.body)
        metodo = data.get("metodo_entrega")
        if metodo not in ["frete", "retirada"]:
            return JsonResponse({
                "status": "erro",
                "mensagem": "Método de entrega inválido."
            }, status=400)
        request.session["metodo_entrega"] = metodo
        request.session.modified = True
        return JsonResponse({
            "status": "ok",
            "mensagem": "Método de entrega selecionado."
        })
    except json.JSONDecodeError:
        return JsonResponse({
            "status": "erro",
            "mensagem": "Dados inválidos."
        }, status=400)