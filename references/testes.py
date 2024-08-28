from payment_api_testes import filtrar_boletos_vencidos, get_customer_details_by_customer_id
import re
from datetime import datetime

def return_expired_invoices_messages():
        
    boletos_vencidos = filtrar_boletos_vencidos()
    messages_list = []

    for boleto in boletos_vencidos:
        
        payment_url = boleto.get('payment_url')
        customer_id = boleto.get('customer_id')
        due_date_br = (datetime.strptime(boleto.get('due_date'), "%Y-%m-%d")).strftime("%d/%m/%Y")
        customer_detail = get_customer_details_by_customer_id(customer_id)
        phone_number = (re.sub(r'\D', '', customer_detail.get('phone_number')))[-9:]
        name = customer_detail.get('full_name')
        full_name = re.sub(r' ', '%20', name)
        whatsapp_message = f"https://api.whatsapp.com/send?phone={phone_number}&text={full_name}%0A%0AA%20mensalidade%20com%20vencimento%20{due_date_br}%20ainda%20consta%20como%20aberto.%0A%0AInformamos%20que%20o%20n%C3%A3o%20pagamento%20dos%20servi%C3%A7os%20podem%20acarretar%20em%20bloqueio%20do%20servi%C3%A7o%20e%20%0Aregistro%20do%20titular%20em%20sistema%20de%20prote%C3%A7%C3%A3o%20ao%20credito.%0A%0ASegue%20o%20boleto:%20{payment_url}%0A%0AAgradecemos%20pela%20sua%20prefer%C3%AAncia%20e%20estamos%20%C3%A0%20disposi%C3%A7%C3%A3o%20para%20qualquer%20d%C3%BAvida%20ou%20suporte%20necess%C3%A1rio.%0A%0AAtenciosamente,%0AEquipe%20Powerlink%0A%0ADesconsiderar%20caso%20o%20pagamento%20j%C3%A1%20tiver%20sido%20realizado"

        message = {
            "name": name,
            "phone_number": phone_number,
            "payment_url": payment_url,
            "due_date_br": due_date_br,
            "whatsapp_message": whatsapp_message
        }
        
        messages_list.append(message)

    return messages_list
