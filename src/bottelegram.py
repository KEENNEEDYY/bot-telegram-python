import os
import telebot
import re

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
    user_state[chat_id] = 'aguardando_cpf'

# Função para validar CPF (considerando apenas números)
def validar_cpf(cpf):
    return bool(re.match(r'^\d{11}$', cpf))

# Captura e valida o CPF do usuário
@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == 'aguardando_cpf')
def captura_cpf(user_message):
    cpf = user_message.text
    chat_id = user_message.chat.id
    
    if validar_cpf(cpf):
        bot.send_message(chat_id, f"CPF {cpf} recebido. Buscando seu boleto...")
        # Chamar funcao para consultar cliente na API de pagamento
        user_state.pop(chat_id)  # Remove o estado do usuário após processar o CPF
    else:
        bot.send_message(chat_id, "CPF inválido. Por favor, informe apenas os 11 dígitos numéricos.")

# Resposta padrão para mensagens não correspondentes a nenhum comando específico
@bot.message_handler(func=lambda message: True)
def answer(user_message):
    bot.reply_to(user_message, default_answer)

bot.polling()
