import os
import telebot
import re
from payment_api.payment_api import get_invoice_urls_by_subscription_id,get_client_id_by_cpf, get_subscription_id_by_client_id, get_active_subscription_id_by_client_id, get_invoice_url_by_subscription_id

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
Você será redirecionado para um de nossos atendentes...
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
    bot.send_message(user_message.chat.id, support_redirect_answer)

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


# Resposta padrão para mensagens não correspondentes a nenhum comando específico
@bot.message_handler(func=lambda message: True)
def answer(user_message):
    bot.reply_to(user_message, default_answer)

bot.polling()
