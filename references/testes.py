from payment_api_testes import filtrar_boletos_vencidos, get_customer_details_by_customer_id
import re

boletos_vencidos = filtrar_boletos_vencidos()

for boleto in boletos_vencidos:
    payment_url = boleto.get('payment_url')
    subscription = boleto.get('subscription')
    customer_id = boleto.get('customer_id')

    phone_number_last_9 = (re.sub(r'\D', '', customer_detail.get('phone_number')))[-9:]

    customer_detail = get_customer_details_by_customer_id(customer_id)
    print(customer_detail.get('full_name'))
    print(customer_detail.get('phone_number'))
    print(boleto.get('payment_url'))
    print('\n\n\n\n')


