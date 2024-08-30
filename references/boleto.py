import requests
import os



api_token = os.getenv('AUTH_PAYMENT_HTTP_TOKEN')
api_base_url = os.getenv('AUTH_PAYMENT_BASE_URL')

print("AUTH_PAYMENT_HTTP_TOKEN:", api_token)
print("AUTH_PAYMENT_BASE_URL:", api_base_url)

def get_client_id_by_cpf(client_cpf, api_url, api_token):
    """
    Faz uma requisição à API de pagamentos para obter o URL do boleto.

    Args:
        client_cpf (str): CPF do cliente.
        api_url (str): URL da API de pagamentos.
        api_token (str): Token de autenticação para a API.

    Returns:
        str: URL do boleto, se encontrado; caso contrário, None.
    """
    headers = {
        'Authorization': f'ApiKey {api_token}',
        'Content-Type': 'application/json'
    }
    params = {'cpf_cnpj': client_cpf}

    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if data['meta']['total_count'] == 1:
            return data['objects'][0]['id']
        else:
            print("Cliente não encontrado ou múltiplos clientes com o mesmo CPF.")
    else:
        print(f"Erro ao buscar o ID do cliente: {response.status_code} - {response.text}")
    return None




def get_subscription_by_client_id(customer_id, api_url, api_token):
    """
    Faz uma requisição à API de pagamentos para obter o URL do boleto.

    Args:
        client_cpf (str): CPF do cliente.
        api_url (str): URL da API de pagamentos.
        api_token (str): Token de autenticação para a API.

    Returns:
        str: URL do boleto, se encontrado; caso contrário, None.
    """
    headers = {
        'Authorization': f'ApiKey {api_token}',
        'Content-Type': 'application/json'
    }
    params = {'customer': customer_id}

    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if data['meta']['total_count'] == 1:
            return data['objects'][0]['id']
        else:
            print("Cliente não encontrado ou múltiplos clientes com o mesmo CPF.")
    else:
        print(f"Erro ao buscar o ID do cliente: {response.status_code} - {response.text}")
    return None



client_cpf = '160.767.476-92'
api_url_client = f'{api_base_url}/customers'
api_url_subscriptions = f'{api_base_url}/subscriptions'



# c
client_id = get_client_id_by_cpf(client_cpf,api_url_client,api_token)
subscription_id = get_subscription_by_client_id(client_id,api_url_subscriptions,api_token)
api_url_invoices = f'{api_base_url}/subscriptions/{subscription_id}/invoices'


def invoices(api_url, api_token):
    """
    Faz uma requisição à API de pagamentos para obter o URL do boleto.

    Args:
        client_cpf (str): CPF do cliente.
        api_url (str): URL da API de pagamentos.
        api_token (str): Token de autenticação para a API.

    Returns:
        str: URL do boleto, se encontrado; caso contrário, None.
    """
    headers = {
        'Authorization': f'ApiKey {api_token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(api_url, headers=headers)
    
    # # Imprime o status da resposta e o texto da resposta para depuração
    # print(f"Status Code: {response.status_code}")
    # print(f"Response Text: {response.text}")

    if response.status_code == 200:
        data = response.json()
        if data['meta']['total_count'] == 1:
            return data['objects'][0]['payment_url']
        else:
            print("Cliente não encontrado ou múltiplos clientes com o mesmo CPF.")
    else:
        print(f"Erro ao buscar o ID do cliente: {response.status_code} - {response.text}")
    return None


def get_url_boletos():
    return invoices(api_url_invoices,api_token)

print(invoices(api_url_invoices,api_token))