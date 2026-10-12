from django.urls import path
from . import views
urlpatterns = [
    path("checkout/",views.checkout,name="checkout"),
    path("pagamento/<int:pedido_id>/",views.pagamento,name="pagamento"),
    path("criar-pagamento/",views.criar_pagamento,name="criar_pagamento"),
    path("pagamento/sucesso/<int:pedido_id>/",views.pagamento_sucesso,name="pagamento_sucesso"),
    path("pagamento/falha/<int:pedido_id>/",views.pagamento_falha,name="pagamento_falha"),
    path("pagamento/pendente/",views.pagamento_pendente,name="pagamento_pendente"),
    path("pagamento/webhook/",views.mercado_pago_webhook,name="mercado_pago_webhook"),
    path("pagamento/<int:pedido_id>/processando/",views.pagamento_processando,name="pagamento_processando"),
    path("pagamento/<int:pedido_id>/consultar/",views.consultar_pagamento,name="consultar_pagamento"),
    path("gerar-etiqueta/<int:pedido_id>/",views.gerar_etiqueta_pedido,name="gerar_etiqueta_pedido"),
    path("imprimir-etiqueta/<int:pedido_id>/",views.imprimir_etiqueta_pedido,name="imprimir_etiqueta_pedido"),
    path("atualizar-tracking/<int:pedido_id>/",views.atualizar_tracking_pedido_view,name="atualizar_tracking_pedido"),
]