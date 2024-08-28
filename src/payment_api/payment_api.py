import requests
import os
import re
from urllib.parse import quote
from datetime import datetime

# Variáveis de ambiente
api_token = os.getenv('AUTH_PAYMENT_HTTP_TOKEN')
api_base_url = os.getenv('AUTH_PAYMENT_BASE_URL')

def get_client_id_by_cpf(client_cpf):
    """
    Obtém o ID do cliente a partir do CPF.

    Args:
        client_cpf (str): CPF do cliente.

    Returns:
        int: ID do cliente, se encontrado; caso contrário, None.
    """
    # Codifica o CPF para a URL
    encoded_cpf = quote(client_cpf)
    api_url = f'{api_base_url}/customers/?cpf_cnpj={encoded_cpf}'
    headers = {
        'Authorization': f'ApiKey {api_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data['meta']['total_count'] == 1:
            return data['objects'][0]['id']
        else:
            print("Cliente não encontrado ou múltiplos clientes com o mesmo CPF.")
    else:
        print(f"Erro ao buscar o ID do cliente: {response.status_code} - {response.text}")
    return None

def get_active_subscription_id_by_client_id(client_id):
    """
    Obtém o ID da assinatura ativa a partir do ID do cliente.

    Args:
        client_id (int): ID do cliente.

    Returns:
        int: ID da assinatura ativa, se encontrado; caso contrário, None.
    """
    api_url = f'{api_base_url}/subscriptions'
    headers = {
        'Authorization': f'ApiKey {api_token}',
        'Content-Type': 'application/json'
    }
    params = {'customer': client_id}

    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        active_subscriptions = [
            sub['id'] for sub in data['objects'] if sub['status'] == 'active'
        ]
        if len(active_subscriptions) == 1:
            return active_subscriptions[0]
        elif len(active_subscriptions) > 1:
            print("Múltiplas assinaturas ativas encontradas.")
            # Retorna o primeiro, lista, ou lida de outra forma
            # Clientes podem ter mais um assinatura 
            return active_subscriptions[0]
        else:
            print("Nenhuma assinatura ativa encontrada.")
    else:
        print(f"Erro ao buscar a assinatura: {response.status_code} - {response.text}")
    return None

def get_subscription_id_by_client_id(client_id):
    """
    Obtém o ID da assinatura a partir do ID do cliente.

    Args:
        client_id (int): ID do cliente.

    Returns:
        int: ID da assinatura, se encontrado; caso contrário, None.
    """
    api_url = f'{api_base_url}/subscriptions'
    headers = {
        'Authorization': f'ApiKey {api_token}',
        'Content-Type': 'application/json'
    }
    params = {'customer': client_id}

    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if data['meta']['total_count'] == 1:
            return data['objects'][0]['id']
        else:
            print("Assinatura não encontrada ou múltiplas assinaturas encontradas.")
    else:
        print(f"Erro ao buscar a assinatura: {response.status_code} - {response.text}")
    return None

def get_invoice_url_by_subscription_id(subscription_id):
    """
    Obtém o URL do boleto a partir do ID da assinatura.

    Args:
        subscription_id (int): ID da assinatura.

    Returns:
        str: URL do boleto, se encontrado; caso contrário, None.
    """
    api_url = f'{api_base_url}/subscriptions/{subscription_id}/invoices'
    headers = {
        'Authorization': f'ApiKey {api_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data['meta']['total_count'] == 1:
            return data['objects'][0]['payment_url']
        else:
            print("Boleto não encontrado ou múltiplos boletos encontrados.")
    else:
        print(f"Erro ao buscar o boleto: {response.status_code} - {response.text}")
    return None

def get_invoice_urls_by_subscription_id(subscription_id):
    """
    Obtém os URLs dos boletos pendentes a partir do ID da assinatura.

    Args:
        subscription_id (int): ID da assinatura.

    Returns:
        list: Lista com os URLs dos boletos pendentes; caso contrário, lista vazia.
    """
    api_url = f'{api_base_url}/subscriptions/{subscription_id}/invoices'
    headers = {
        'Authorization': f'ApiKey {api_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        pending_urls = [
            invoice['payment_url'] 
            for invoice in data['objects'] 
            if invoice['status'] == 'pending'
        ]
        if pending_urls:
            return pending_urls
        else:
            print("Nenhum boleto pendente encontrado.")
    else:
        print(f"Erro ao buscar os boletos: {response.status_code} - {response.text}")
    return []

def return_expired_invoices():
    """
    Obtém a lista de boletos pendentes 

    Returns:
        list: Lista com os URLs dos boletos pendentes; caso contrário, lista vazia.
    """
    api_url = f'{api_base_url}/invoices'
    headers = {
        'Authorization': f'ApiKey {api_token}',
        'Content-Type': 'application/json'
    }

    params = {'status': 'pending', 'limit': '100'}

    response = requests.get(api_url, headers=headers, params=params)
    # Verifica se a resposta foi bem-sucedida
    if response.status_code != 200:
        print(f"Erro na requisição: {response.status_code} - {response.text}")
        return []
    

    try:
        data = response.json()
    except ValueError:
        print("Erro ao converter a resposta para JSON")
        return []

    boletos_vencidos = []
    hoje = datetime.now().date()

    for boleto in data.get('objects', []):
        if boleto.get('status') == 'pending':
            due_date = datetime.strptime(boleto.get('due_date'), "%Y-%m-%d").date()
            if due_date < hoje:
                boletos_vencidos.append(boleto)
    
    return boletos_vencidos


def return_all_invoices():
    """
    Obtém a lista de boletos pendentes 

    Returns:
        list: Lista com os URLs dos boletos pendentes; caso contrário, lista vazia.
    """
    api_url = f'{api_base_url}/invoices'
    headers = {
        'Authorization': f'ApiKey {api_token}',
        'Content-Type': 'application/json'
    }

    params = {'status': 'pending', 'limit': '100'}

    response = requests.get(api_url, headers=headers, params=params)
    # Verifica se a resposta foi bem-sucedida
    if response.status_code != 200:
        print(f"Erro na requisição: {response.status_code} - {response.text}")
        return []
    

    try:
        data = response.json()
    except ValueError:
        print("Erro ao converter a resposta para JSON")
        return []

    todos_boletos = []
    hoje = datetime.now().date()

    for boleto in data.get('objects', []):
        if boleto.get('status') == 'pending':
            due_date = datetime.strptime(boleto.get('due_date'), "%Y-%m-%d").date()
            if  hoje < due_date:
                todos_boletos.append(boleto)
    
    return todos_boletos

def return_subscriptions_from_expired_invoices():
    """
    Obtém a lista de boletos pendentes 

    Returns:
        list: Lista com os URLs dos boletos pendentes; caso contrário, lista vazia.
    """
    api_url = f'{api_base_url}/invoices'
    headers = {
        'Authorization': f'ApiKey {api_token}',
        'Content-Type': 'application/json'
    }

    params = {'status': 'pending', 'limit': '100'}

    response = requests.get(api_url, headers=headers, params=params)
    # Verifica se a resposta foi bem-sucedida
    if response.status_code != 200:
        print(f"Erro na requisição: {response.status_code} - {response.text}")
        return []
    

    try:
        data = response.json()
    except ValueError:
        print("Erro ao converter a resposta para JSON")
        return []

    boletos_vencidos = []
    hoje = datetime.now().date()

    for boleto in data.get('objects', []):
        if boleto.get('status') == 'pending':
            due_date = datetime.strptime(boleto.get('due_date'), "%Y-%m-%d").date()
            if due_date < hoje:
                boletos_vencidos.append(boleto)
    
    return boletos_vencidos

def get_customer_details_by_customer_id(customer_id):

    """
    Obtém o dados do cliente a partir de seu Id.

    Args:
        customer_id (str): id do cliente.

    Returns:
        detalhes do client, se encontrado; caso contrário, None.
    """
    
    api_url = f'{api_base_url}/customers/{customer_id}'
    headers = {
        'Authorization': f'ApiKey {api_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data:
            return data
        else:
            print("Erro ao encontrar o ciente")
    else:
        print(f"Erro {response.status_code} - {response.text}")
    return None

def return_expired_invoices_messages():
        
    boletos_vencidos = return_expired_invoices()
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




def return_expired_all_invoices_messages():
        
    boletos_vencidos = return_all_invoices()
    messages_list = []

    for boleto in boletos_vencidos:
        
        payment_url = boleto.get('payment_url')
        customer_id = boleto.get('customer_id')
        due_date_br = (datetime.strptime(boleto.get('due_date'), "%Y-%m-%d")).strftime("%d/%m/%Y")
        customer_detail = get_customer_details_by_customer_id(customer_id)
        phone_number = (re.sub(r'\D', '', customer_detail.get('phone_number')))[-9:]
        name = customer_detail.get('full_name')
        full_name = re.sub(r' ', '%20', name)
        whatsapp_message = f"https://api.whatsapp.com/send?phone={phone_number}&text=Ol%c3%a1%20{full_name}%2c%0a%0aEstimado%20cliente%20Powerlink%2c%0a%0aGostar%c3%adamos%20de%20informar%20que%20a%20sua%20fatura%20de%20vencimento%20{due_date_br}%20j%c3%a1%20est%c3%a1%20dispon%c3%advel%20para%20pagamento.%20Voc%c3%aa%20pode%20acess%c3%a1-la%20atrav%c3%a9s%20do%20link%20abaixo%3a%0a%0a{payment_url}%0a%0aAgradecemos%20pela%20sua%20prefer%c3%aancia%20e%20estamos%20%c3%a0%20disposi%c3%a7%c3%a3o%20para%20qualquer%20d%c3%bavida%20ou%20suporte%20necess%c3%a1rio.%0a%0aAtenciosamente%2c%0aEquipe%20Powerlink%0a%0aSe%20precisar%20de%20mais%20alguma%20coisa%2c%20estou%20%c3%a0%20disposi%c3%a7%c3%a3o%21"

        message = {
            "name": name,
            "phone_number": phone_number,
            "payment_url": payment_url,
            "due_date_br": due_date_br,
            "whatsapp_message": whatsapp_message
        }
        
        messages_list.append(message)

    return messages_list




