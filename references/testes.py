from payment_api_testes import filtrar_boletos_vencidos


boletos_vencidos = filtrar_boletos_vencidos()

for boleto in boletos_vencidos:
    print(boleto.get('payment_url') + boleto.get('subscription'))
