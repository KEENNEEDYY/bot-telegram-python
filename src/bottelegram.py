import os
import telebot

api_token = os.getenv('AUTH_TELEGRAM_HTTP_TOKEN')

bot = telebot.TeleBot(api_token)

default_answer = """
Olá seja bem vindo ao atendimento Powerlink Company...
Escolha uma opção (CLIQUE NO ITEM): 

/opcao1 - Contratar nossos serviços
/opcao2 - Suporte
/opcao3 - Realizar pagamento
"""

join_service_answer = """
Informe o CPF do titular do contrato!
"""


@bot.message_handler(commands=["opcao1"])
def opcao1(user_message):
    pass

@bot.message_handler(commands=["opcao2"])
def opcao2(user_message):
    pass

@bot.message_handler(commands=["opcao3"])
def opcao3(user_message):
    bot.send_message(user_message.chat.id, join_service_answer)
    # CRIAR REGRA DE REGEX PARA PEGAR SOMENTE NUMERO






def checkMessage(message):
    return True

@bot.message_handler(func=checkMessage)
def answer(user_message):
    bot.reply_to(user_message, default_answer)



bot.polling()