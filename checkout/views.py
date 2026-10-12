from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect,render
from cart.cart import Cart
from .services import validar_frete_selecionado,criar_pedido, processar_pagamento_aprovado, comprar_e_gerar_etiqueta, atualizar_tracking_pedido,descriptografar_documento
import mercadopago
from django.views.decorators.http import require_POST
import os
from django.conf import settings
from .models import Pedido
from core.models import MelhorEnvioToken
from core.melhor_envio import MelhorEnvioAPI,obter_token_melhor_envio
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.http import JsonResponse, HttpResponseForbidden, Http404
import json
from django.utils import timezone
from django.urls import reverse
from mercadopago.config import RequestOptions
import uuid
from django_smart_ratelimit import ratelimit

@login_required(login_url="/login/")
def checkout(request):
    cart = Cart(request)
    cart_produtos = cart.get_produtos()
    if not cart_produtos:
        request.session["erro"] = "Seu carrinho está vazio."
        return redirect("cart")
    metodo_entrega = request.session.get(
        "metodo_entrega",
        "frete"
    )
    if metodo_entrega == "frete":
        sucesso, cotacao, opcao, erro = validar_frete_selecionado(request)
        if not sucesso:
            request.session["erro"] = erro
            request.session.pop(
                "frete_selecionado",
                None
            )
            request.session.modified = True
            return redirect("cart")
        frete = Decimal(str(opcao.preco))
    else:
        metodo_entrega = "retirada"
        cotacao = None
        opcao = None
        frete = Decimal("0.00")
    subtotal = sum(
        Decimal(str(item["subtotal"]))
        for item in cart_produtos
    )
    total = subtotal + frete
    perfil = request.user.perfil
    if metodo_entrega == "retirada":
        dados_cliente = {
            "nome": request.user.username,
            "email": request.user.email,
            "telefone": perfil.telefone or "",
            "cep": None,
            "endereco": None,
            "numero": None,
            "complemento": None,
            "bairro": None,
            "cidade": None,
            "estado": None,
        }
        try:
            pedido = criar_pedido(request,dados_cliente)
        except ValueError as erro:
            request.session["erro"] = str(erro)
            request.session.pop("frete_selecionado",None)
            request.session.modified = True
            return redirect("cart")
        request.session.pop("frete_selecionado",None)
        request.session.pop("metodo_entrega",None)
        request.session.modified = True
        return redirect( "pagamento", pedido_id=pedido.id)
    if request.method == "GET":
        return render(request,"checkout.html",
            {
                "cart_items": cart_produtos,
                "subtotal": subtotal,
                "frete": frete,
                "total": total,
                "frete_opcao": opcao,
                "cotacao": cotacao,
                "perfil": perfil,
                "metodo_entrega": metodo_entrega,
            }
        )
    if request.method == "POST":
        nome = request.POST.get("nome","").strip()
        email = request.user.email
        telefone = "19986023865"
        cep = request.POST.get("cep","").strip()
        endereco = request.POST.get("endereco","").strip()
        numero = request.POST.get("numero","").strip()
        complemento = request.POST.get("complemento","").strip()
        bairro = request.POST.get("bairro","").strip()
        cidade = request.POST.get("cidade","").strip()
        estado = request.POST.get("estado","").strip().upper()
        if not all([nome,email,telefone,cep,endereco,numero,bairro,cidade,estado]):
            return render(request, "checkout.html",
                {
                    "cart_items": cart_produtos,
                    "subtotal": subtotal,
                    "frete": frete,
                    "total": total,
                    "frete_opcao": opcao,
                    "cotacao": cotacao,
                    "perfil": perfil,
                    "metodo_entrega": metodo_entrega,
                    "erro": "Preencha todos os campos obrigatórios.",
                }
            )
        cep_limpo = "".join(
            c for c in cep
            if c.isdigit()
        )
        if cep_limpo != cotacao.cep_destino:
            return render(request,"checkout.html",
                {
                    "status": "erro",
                    "cart_items": cart_produtos,
                    "subtotal": subtotal,
                    "frete": frete,
                    "total": total,
                    "frete_opcao": opcao,
                    "cotacao": cotacao,
                    "perfil": perfil,
                    "metodo_entrega": metodo_entrega,
                    "mensagem": "O CEP informado é diferente do CEP utilizado no cálculo do frete.",
                },status=400)
        dados_cliente = {
            "nome": nome,
            "email": email,
            "telefone": telefone,
            "cep": cep_limpo,
            "endereco": endereco,
            "numero": numero,
            "complemento": complemento,
            "bairro": bairro,
            "cidade": cidade,
            "estado": estado,

        }
        try:
            pedido = criar_pedido(request,dados_cliente)
        except ValueError as erro:
            request.session["erro"] = str(erro)
            request.session.pop("frete_selecionado",None)
            request.session.modified = True
            return redirect("cart")
        request.session.pop("frete_selecionado", None)
        request.session.pop("metodo_entrega",None)
        request.session.modified = True
        return redirect("pagamento",pedido_id=pedido.id)
    raise Http404()

@login_required(login_url="/login/")
def pagamento(request, pedido_id):
    try:
        pedido = Pedido.objects.get(id=pedido_id,usuario=request.user)
    except Pedido.DoesNotExist:
        return redirect("cart")
    if pedido.status != "aguardando_pagamento":
        return render(request,"pagamento.html",{
                "status" : "erro",
                "pedido": pedido,
                "erro": "Este pedido não está disponível para pagamento."
            }
        )
    return render(request,"pagamento.html",{
            "pedido": pedido,
            "mercado_pago_public_key": os.getenv("MERCADO_PAGO_PUBLIC_KEY")
        }
    )

@login_required(login_url="/login/")
def criar_pagamento(request):
    if request.method != "POST":
        raise Http404()
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({
            "status": "erro",
            "codigo": "requisicao_invalida",
            "mensagem": "Não foi possível processar a solicitação."
        }, status=400)
    pedido_id = data.get("pedido_id")
    if not pedido_id:
        return JsonResponse({
            "status": "erro",
            "codigo": "pedido_nao_informado",
            "mensagem": "Pedido não informado."
        }, status=400)
    try:
        pedido = Pedido.objects.get(id=pedido_id,usuario=request.user)
    except Pedido.DoesNotExist:
        return JsonResponse({
            "status": "erro",
            "codigo": "pedido_nao_encontrado",
            "mensagem": "Pedido não encontrado."
        }, status=404)
    if pedido.status != "aguardando_pagamento":
        return JsonResponse({
            "status": "erro",
            "codigo": "pedido_indisponivel",
            "mensagem": "Este pedido não está aguardando pagamento."
        }, status=400)
    payment_method_id = str(
        data.get("payment_method_id") or ""
    ).strip().lower()
    if not payment_method_id:
        return JsonResponse({
            "status": "erro",
            "codigo": "metodo_pagamento_nao_informado",
            "mensagem": "Método de pagamento não informado."
        }, status=400)
    try:
        transaction_amount = Decimal(str(pedido.total))
    except (InvalidOperation, TypeError, ValueError):
        return JsonResponse({
            "status": "erro",
            "codigo": "valor_invalido",
            "mensagem": "O valor do pedido é inválido."
        }, status=400)
    if transaction_amount <= 0:
        return JsonResponse({
            "status": "erro",
            "codigo": "valor_invalido",
            "mensagem": "O valor do pedido deve ser maior que zero."
        }, status=400)
    payer = data.get("payer")
    if not isinstance(payer, dict):
        payer = {}
    email_pagador = (
        payer.get("email")
        or pedido.email_cliente
        or getattr(request.user, "email", None)
    )
    if not email_pagador:
        return JsonResponse({
            "status": "erro",
            "codigo": "email_nao_informado",
            "mensagem": "E-mail do pagador não informado."
        }, status=400)
    email_pagador = str(email_pagador).strip()
    nome_completo = (
        payer.get("first_name")
        or pedido.nome_cliente
        or request.user.get_full_name()
        or request.user.username
        or "Cliente"
    )
    nome_completo = str(nome_completo).strip()
    partes_nome = nome_completo.split(" ", 1)
    first_name = partes_nome[0] or "Cliente"
    last_name = (
        partes_nome[1].strip()
        if len(partes_nome) > 1 and partes_nome[1].strip()
        else "Sobrenome"
    )
    def limpar_cpf(valor):
        if valor is None:
            return ""
        return "".join(
            filter(str.isdigit, str(valor))
        )
    def cpf_valido(cpf):
        cpf = limpar_cpf(cpf)
        if len(cpf) != 11:
            return False
        if cpf == cpf[0] * 11:
            return False
        soma = sum(
            int(cpf[i]) * (10 - i)
            for i in range(9)
        )
        digito_1 = (soma * 10) % 11
        if digito_1 == 10:
            digito_1 = 0
        if digito_1 != int(cpf[9]):
            return False
        soma = sum(
            int(cpf[i]) * (11 - i)
            for i in range(10)
        )
        digito_2 = (soma * 10) % 11
        if digito_2 == 10:
            digito_2 = 0
        return digito_2 == int(cpf[10])
    documento_bruto = None
    perfil = getattr(request.user, "perfil", None)
    if perfil and getattr(perfil, "documento", None):
        try:
            documento_bruto = descriptografar_documento(perfil.documento)
        except Exception:
            documento_bruto = perfil.documento
    cpf_perfil = limpar_cpf(documento_bruto)
    cpf_frontend = ""
    identification = payer.get("identification")
    if isinstance(identification, dict):
        cpf_frontend = limpar_cpf(identification.get("number"))
    if not cpf_frontend:
        cpf_frontend = limpar_cpf(payer.get("cpf"))
    if not cpf_frontend:
        cpf_frontend = limpar_cpf(data.get("cpf"))
    cpf_limpo = ""
    if cpf_valido(cpf_perfil):
        cpf_limpo = cpf_perfil
    elif payment_method_id != "pix" and cpf_valido(cpf_frontend):
        cpf_limpo = cpf_frontend
    if not cpf_limpo:
        return JsonResponse({
            "status": "erro",
            "codigo": "cpf_obrigatorio",
            "mensagem": "Para finalizar a compra, você precisa informar um CPF válido.",
            "acao": "atualizar_cpf",
            "redirect_url": "/perfil/"
        }, status=400)
    payment_data = {
        "transaction_amount": float(transaction_amount),
        "description": f"Pedido #{pedido.id} - Cerâmica Barroá",
        "payment_method_id": payment_method_id,
        "payer": {
            "email": email_pagador,
            "first_name": first_name,
            "last_name": last_name,
            "identification": {
                "type": "CPF",
                "number": cpf_limpo
            }
        },
        "external_reference": str(pedido.id),
    }
    if payment_method_id != "pix":
        token = data.get("token")
        if not token:
            return JsonResponse({
                "status": "erro",
                "codigo": "token_cartao_nao_informado",
                "mensagem": "Não foi possível validar os dados do cartão. Tente novamente."
            }, status=400)
        installments_raw = data.get("installments")
        try:
            installments = int(installments_raw)
        except (TypeError, ValueError):
            return JsonResponse({
                "status": "erro",
                "codigo": "parcelas_invalidas",
                "mensagem": "Número de parcelas inválido."
            }, status=400)
        if installments < 1:
            return JsonResponse({
                "status": "erro",
                "codigo": "parcelas_invalidas",
                "mensagem": "Número de parcelas inválido."
            }, status=400)
        valor_minimo_parcela = Decimal("30.00")
        max_installments = min(int(transaction_amount // valor_minimo_parcela),18)
        max_installments = max(1, max_installments)
        if installments > max_installments:
            return JsonResponse({
                "status": "erro",
                "codigo": "limite_parcelas",
                "mensagem": f"Para este pedido, o máximo permitido é {max_installments}x.",
                "max_installments": max_installments
            }, status=400)
        payment_data["token"] = str(token)
        payment_data["installments"] = installments
        issuer_id = data.get("issuer_id")
        if issuer_id:
            payment_data["issuer_id"] = str(issuer_id)
    try:
        sdk_token = os.getenv("SDK")
        if not sdk_token:
            print("DEBUG - [ERRO MP] SDK não configurado.")
            return JsonResponse({
                "status": "erro",
                "codigo": "configuracao_pagamento",
                "mensagem": "O pagamento não está disponível no momento."
            }, status=500)
        request_options = RequestOptions()
        request_options.custom_headers = {
            "x-idempotency-key": str(uuid.uuid4())
        }
        sdk = mercadopago.SDK(sdk_token)
        payment_response = sdk.payment().create( payment_data,request_options)
        response_status = payment_response.get("status")
        payment = payment_response.get("response") or {}
        if response_status not in [200, 201]:
            mensagem_mp = payment.get("message")
            causas = payment.get("cause")
            print(
                f"DEBUG - [ERRO MP] "
                f"HTTP={response_status} "
                f"payment={payment} "
                f"cause={causas}"
            )
            mensagem_usuario = "Não foi possível processar o pagamento. Verifique os dados informados e tente novamente."
            if mensagem_mp:
                mensagem_usuario = str(mensagem_mp)
            return JsonResponse({
                "status": "erro",
                "codigo": "erro_mercado_pago",
                "mensagem": mensagem_usuario
            }, status=400)
        payment_id = payment.get("id")
        payment_status = payment.get("status")
        status_detail = payment.get("status_detail")
        if not payment_id:
            print(f"DEBUG - [ERRO MP] Pagamento criado sem ID: {payment}")
            return JsonResponse({
                "status": "erro",
                "codigo": "pagamento_sem_id",
                "mensagem": "O pagamento não pôde ser identificado. Tente novamente."
            }, status=500)
        transaction_data = (payment.get("point_of_interaction", {}).get("transaction_data", {}))
        qr_code_base64 = transaction_data.get("qr_code_base64")
        ticket_url = transaction_data.get("ticket_url")
        qr_code = transaction_data.get("qr_code")
        request.session["pix_payment"] = {
            "payment_id": str(payment_id),
            "qr_code": qr_code,
            "qr_code_base64": qr_code_base64,
            "ticket_url": ticket_url,
            "pedido_id": pedido.id,
        }
        pedido.mp_payment_id = str(payment_id)
        pedido.mp_status = payment_status
        pedido.mp_status_detail = status_detail
        pedido.atualizado_em = timezone.now()
        pedido.save(
            update_fields=[
                "mp_payment_id",
                "mp_status",
                "mp_status_detail",
                "atualizado_em"
            ]
        )
        return JsonResponse({
            "status": "ok",
            "mensagem": "Pagamento criado.",
            "payment_status": payment_status,
            "payment_id": str(payment_id),
            "redirect_url": (
                reverse("pagamento_pendente")
                if payment_method_id == "pix"
                else reverse(
                    "pagamento_processando",
                    kwargs={"pedido_id": pedido.id}
                )
            )
        })
    except Exception as e:
        print(f"DEBUG - [ERRO PAGAMENTO] {type(e).__name__}: {repr(e)}")
        return JsonResponse({
            "status": "erro",
            "codigo": "erro_comunicacao_pagamento",
            "mensagem": "Não foi possível comunicar com o serviço de pagamento. Tente novamente."
        }, status=500)

@login_required(login_url="/login/")
def consultar_pagamento(request, pedido_id):
    try:
        pedido = Pedido.objects.get(id=pedido_id,usuario=request.user)
    except Pedido.DoesNotExist:
        return JsonResponse({
                "status": "erro",
                "mensagem": "Pedido não encontrado."
            },status=400)
    if not pedido.mp_payment_id:
        return JsonResponse({
                "status": "erro",
                "mensagem": "Pagamento ainda não foi criado."
            },status=400)
    sdk = mercadopago.SDK(os.getenv("SDK"))
    payment_response = sdk.payment().get(pedido.mp_payment_id)
    payment = payment_response.get("response",{})
    payment_status = payment.get("status")
    if payment_status == "approved":
        processar_pagamento_aprovado(pedido,payment)
        return JsonResponse({
            "status": "approved",
            "redirect_url": reverse(
                "pagamento_sucesso",
                args=[pedido.id]
            )
        })
    if payment_status in ["rejected","cancelled"]:
        return JsonResponse({
            "status": payment_status,
            "redirect_url": reverse(
                "pagamento_falha",
                args=[pedido.id]
            )
        })
    return JsonResponse({
        "status": payment_status,
        "mensagem": "Pagamento ainda está sendo processado."
    })

@login_required(login_url="/login/")
def pagamento_processando(request, pedido_id):
    try:
        pedido = Pedido.objects.get(id=pedido_id,usuario=request.user)
    except Pedido.DoesNotExist:
        return redirect("cart")
    return render(request,"pagamento/processando.html",{
            "pedido": pedido
        }
    )

@login_required(login_url="/login/")
def pagamento_sucesso(request, pedido_id):
    try:
        pedido = Pedido.objects.get(id=pedido_id,usuario=request.user)
    except Pedido.DoesNotExist:
        return redirect("cart")
    cart = Cart(request)
    cart.cart.clear()
    request.session.modified = True
    return render(request,"pagamento/sucesso.html",{
            "pedido": pedido
        }
    )

@login_required(login_url="/login/")
def pagamento_falha(request, pedido_id):
    try:
        pedido = Pedido.objects.get(id=pedido_id,usuario=request.user)
    except Pedido.DoesNotExist:
        return redirect("cart")
    return render(request,"pagamento/falha.html",{
            "pedido": pedido
        }
    )

@login_required(login_url="/login/")
def pagamento_pendente(request):
    pix_payment = request.session.get("pix_payment")
    if not pix_payment:
        return redirect("cart")
    pedido_id = pix_payment.get("pedido_id")
    try:
        pedido = Pedido.objects.get(id=pedido_id,usuario=request.user)
    except Pedido.DoesNotExist:
        return redirect("cart")
    return render(request,"pagamento/pendente.html",{
            "pix_payment": pix_payment,
            "qr_code": pix_payment.get("qr_code"),
            "qr_code_base64": pix_payment.get("qr_code_base64"),
            "ticket_url": pix_payment.get("ticket_url"),
            "pedido_id": pix_payment.get("pedido_id"),
        }
    )

@csrf_exempt
def mercado_pago_webhook(request):
    if request.method != "POST":
        raise Http404()
    try:
        data = json.loads(request.body)
        event_type = data.get("type")
        if event_type != "payment":
            return JsonResponse({"status": "ok"})
        payment_id = data.get("data", {}).get("id")
        if not payment_id:
            return JsonResponse({"status": "ok"})
        sdk = mercadopago.SDK(os.getenv("SDK"))
        payment_response = sdk.payment().get(payment_id)
        payment = payment_response.get("response", {})
        if payment.get("status") != "approved":
            return JsonResponse({"status": "ok"})
        pedido_id = payment.get("external_reference")
        if not pedido_id:
            return JsonResponse({"status": "ok"})
        try:
            pedido = Pedido.objects.get(id=pedido_id)
        except Pedido.DoesNotExist:
            return JsonResponse({"status": "ok"})
        processar_pagamento_aprovado(pedido,payment)
        return JsonResponse({"status": "ok"})
    except Exception as erro:
        return JsonResponse({"status": "erro"},status=500)

@login_required(login_url="/login/")
def gerar_etiqueta_pedido(request, pedido_id):
    if not request.user.is_staff:
        raise Http404()
    pedido = get_object_or_404(Pedido, id=pedido_id)
    try:
        comprar_e_gerar_etiqueta(pedido.id)
        pedido.refresh_from_db()
        pedido.etiqueta_paga = True
        pedido.save(update_fields=["etiqueta_paga"])
        pedido.refresh_from_db()
    except ValueError as erro:
        messages.error(request, "Erro ao gerar/pagar a etiqueta, verificar os logs")  
        return redirect("homePerfil")
    messages.success(request,f"Etiqueta do pedido #{pedido.id} gerada com sucesso.")
    return redirect("homePerfil")

@login_required(login_url="/login/")
def imprimir_etiqueta_pedido(request, pedido_id):
    if not request.user.is_staff:
        raise Http404()
    pedido = Pedido.objects.get(id=pedido_id)
    if not pedido.melhor_envio_order_id:
        messages.error(request,"Este pedido não possui um envio no Melhor Envio.")
        return redirect("detalhe_pedido", pedido_id=pedido.id)
    access_token = obter_token_melhor_envio()
    if not access_token:
        messages.error("Melhor Envio não está conectado.")
        return redirect("detalhe_pedido", pedido_id=pedido.id)
    api = MelhorEnvioAPI(access_token=access_token)
    response = api.imprimir_etiqueta([pedido.melhor_envio_order_id],mode="public")
    if response.status_code not in (200, 201):
        messages.error(request,"Erro ao imprimir etiqueta: {response.text}")
        return redirect("detalhe_pedido", pedido_id=pedido.id)
    dados = response.json()
    url_etiqueta = dados.get("url") if isinstance(dados, dict) else dados
    if url_etiqueta:
        pedido.refresh_from_db()
        pedido.etiqueta_url = url_etiqueta
        pedido.save(update_fields=["etiqueta_url"])
        return redirect(url_etiqueta)
    messages.error(request, "URL da etiqueta não foi encontrada na resposta do Melhor Envio.")
    return redirect("detalhe_pedido", pedido_id=pedido.id)

@login_required(login_url="/login/")
def atualizar_tracking_pedido_view(request, pedido_id):
    if not request.user.is_staff:
        raise Http404()
    pedido = Pedido.objects.get(id=pedido_id)
    try:
        atualizar_tracking_pedido(pedido.id)
        messages.success(request,"Rastreamento atualizado com sucesso.")
    except ValueError as erro:
        messages.error(request, str(erro))
    return redirect("homePerfil")