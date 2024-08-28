import os
import telebot
import re
from payment_api.payment_api import return_expired_all_invoices_messages,return_expired_invoices_messages, get_invoice_urls_by_subscription_id,get_client_id_by_cpf, get_subscription_id_by_client_id, get_active_subscription_id_by_client_id, get_invoice_url_by_subscription_id

# Configurações do bot
api_token = os.getenv('AUTH_TELEGRAM_HTTP_TOKEN')
bot = telebot.TeleBot(api_token)

default_answer = """
Olá, seja bem-vindo ao atendimento Powerlink Company...
Escolha uma opção (CLIQUE NO ITEM): 

/opcao1 - Contratar nossos serviços
/opcao2 - Suporte
/opcao3 - Realizar pagamento
"""

request_cpf_answer = """
Informe o CPF do titular do contrato (somente números)!
"""

support_redirect_answer = """
Acesso nosso suporte pelo facebook messager através do link a seguir:

https://m.me/184164441453938?source=qr_link_share
"""
sales_redirect_answer = """
Clique no link a seguir para ter acesso ao universo de soluções que a Powerlink pode lhe oferecer: 

https://api.whatsapp.com/send?phone=5531989870427&text=Ol%C3%A1,%20vi%20seu%20an%C3%BAncio%20pelo%20site%20e%20gostaria%20de%20conhecer%20seus%20planos%20para%20rastreamento%20veicular.
"""

def format_cpf(cpf):
    """
    Formata um CPF sem caracteres especiais para o formato com pontos e hífen.

    Args:
        cpf (str): CPF sem formatação (apenas números).

    Returns:
        str: CPF formatado no formato "XXX.XXX.XXX-XX".
    """
    if len(cpf) != 11 or not cpf.isdigit():
        raise ValueError("O CPF deve ter exatamente 11 dígitos numéricos.")
    
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

# Dicionário para armazenar o estado dos usuários
user_state = {}

# Comando para opção 1
@bot.message_handler(commands=["opcao1"])
def opcao1(user_message):
    bot.send_message(user_message.chat.id, sales_redirect_answer)

# Comando para opção 2
@bot.message_handler(commands=["opcao2"])
def opcao2(user_message):
    bot.send_message(user_message.chat.id, support_redirect_answer)

# Comando para opção 3
@bot.message_handler(commands=["opcao3"])
def opcao3(user_message):
    chat_id = user_message.chat.id
    bot.send_message(chat_id, request_cpf_answer)
    
    # Marca o estado do usuário como "aguardando CPF"
    user_state[chat_id] = 'aguardando_cpf_boleto'


# Comando para opção 4
@bot.message_handler(commands=["cobrancas_vencidas"])
def opcao3(user_message):
    chat_id = user_message.chat.id    
    # Marca o estado do usuário como "aguardando CPF"
    user_state[chat_id] = 'mensagem_de_cobranca'
    mensagem_de_cobranca(user_message)

@bot.message_handler(commands=["todas_as_cobrancas"])
def opcao3(user_message):
    chat_id = user_message.chat.id    
    # Marca o estado do usuário como "aguardando CPF"
    user_state[chat_id] = 'todas_as_cobrancas'
    mensagem_todas_as_cobrancas(user_message)

# Função para validar CPF (considerando apenas números)
def validar_cpf(cpf):
    return bool(re.match(r'^\d{11}$', cpf))

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == 'aguardando_cpf_boleto')
def captura_cpf(user_message):
    cpf = user_message.text
    chat_id = user_message.chat.id
    
    if validar_cpf(cpf):
        bot.send_message(chat_id, f"CPF {cpf} recebido. Buscando seus boletos...")

        # Obter ID do cliente
        client_id = get_client_id_by_cpf(format_cpf(cpf))
        if client_id:
            # Obter ID da assinatura
            subscription_id = get_active_subscription_id_by_client_id(client_id)
            
            if subscription_id:
                # Obter URLs dos boletos
                boletos_urls = get_invoice_urls_by_subscription_id(subscription_id)
                if boletos_urls:
                    for url in boletos_urls:
                        bot.send_message(chat_id, f"Aqui está um dos seus boletos pendentes: {url}")
                else:
                    bot.send_message(chat_id, "Desculpe, não consegui encontrar boletos pendentes.")
            else:
                bot.send_message(chat_id, "Desculpe, não consegui encontrar a assinatura.")
        else:
            bot.send_message(chat_id, "Desculpe, não consegui encontrar o cliente.")
        
        # Remove o estado do usuário após processar o CPF
        user_state.pop(chat_id)  
    else:
        bot.send_message(chat_id, "CPF inválido. Por favor, informe apenas os 11 dígitos numéricos.")


@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == 'mensagem_de_cobranca')
def mensagem_de_cobranca(user_message):
    chat_id = user_message.chat.id
    bot.send_message(chat_id, f"Acionado solicitaçao de mensagens de cobranca...")

    mensagens = return_expired_invoices_messages()

    if mensagens:
        # Envia cada mensagem de cobrança ao usuário
        for mensagem in mensagens:
            # Extraindo a mensagem completa para o WhatsApp
            name = mensagem.get('name', 'Mensagem não disponível')
            phone_number = mensagem.get('phone_number', 'Mensagem não disponível')
            due_date_br = mensagem.get('due_date_br', 'Mensagem não disponível')
            whatsapp_message = mensagem.get('whatsapp_message', 'Mensagem não disponível')
            bot_message = f"""
CLIENTE = {name}
NUMERO DE TELEFONE = {phone_number}
DATA DE VENCIMENTO = {due_date_br}
Redirecionamento para whatsapp:
{whatsapp_message}

"""
            bot.send_message(chat_id, bot_message)
        
        # Remove o estado do usuário após o envio das mensagens
        user_state.pop(chat_id)
    else:
        bot.send_message(chat_id, "Nenhuma mensagem de cobrança encontrada.")
        user_state.pop(chat_id)


@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == 'todas_as_cobrancas')
def mensagem_todas_as_cobrancas(user_message):
    chat_id = user_message.chat.id
    bot.send_message(chat_id, f"Acionado solicitaçao de mensagens de todas as cobranca...")

    mensagens = return_expired_all_invoices_messages()

    if mensagens:
        # Envia cada mensagem de cobrança ao usuário
        for mensagem in mensagens:
            # Extraindo a mensagem completa para o WhatsApp
            name = mensagem.get('name', 'Mensagem não disponível')
            phone_number = mensagem.get('phone_number', 'Mensagem não disponível')
            due_date_br = mensagem.get('due_date_br', 'Mensagem não disponível')
            whatsapp_message = mensagem.get('whatsapp_message', 'Mensagem não disponível')
            bot_message = f"""
CLIENTE = {name}
NUMERO DE TELEFONE = {phone_number}
DATA DE VENCIMENTO = {due_date_br}
Redirecionamento para whatsapp:
{whatsapp_message}

"""
            bot.send_message(chat_id, bot_message)
        
        # Remove o estado do usuário após o envio das mensagens
        user_state.pop(chat_id)
    else:
        bot.send_message(chat_id, "Nenhuma mensagem de cobrança encontrada.")
        user_state.pop(chat_id)


# Resposta padrão para mensagens não correspondentes a nenhum comando específico
@bot.message_handler(func=lambda message: True)
def answer(user_message):
    bot.reply_to(user_message, default_answer)

bot.polling()
