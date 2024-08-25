from payment_api import get_client_id_by_cpf, get_subscription_id_by_client_id, get_invoice_url_by_subscription_id

def get_boleto_url(client_cpf):
    """
    Obtém o URL do boleto a partir do CPF do cliente.

    Args:
        client_cpf (str): CPF do cliente.

    Returns:
        str: URL do boleto, se encontrado; caso contrário, None.
    """
    client_id = get_client_id_by_cpf(client_cpf)
    if client_id:
        subscription_id = get_subscription_id_by_client_id(client_id)
        if subscription_id:
            return get_invoice_url_by_subscription_id(subscription_id)
    return None

if __name__ == "__main__":
    client_cpf = '160.767.476-92'  # Exemplo de CPF
    boleto_url = get_boleto_url(client_cpf)
    if boleto_url:
        print(f"URL do Boleto: {boleto_url}")
    else:
        print("Não foi possível obter o URL do boleto.")
