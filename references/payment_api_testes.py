import requests
import os
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
    print(client_id)

    response = requests.get(api_url, headers=headers, params=params)
    print(response)

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
    print(client_id)

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


def filtrar_boletos_vencidos():
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

