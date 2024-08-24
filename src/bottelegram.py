import os
import telebot

api_token = os.getenv('AUTH_TELEGRAM_HTTP_TOKEN')

bot = telebot.TeleBot(api_token)

default_answer = (
    "Olá seja bem vindo ao atendimento Powerlink Company...\r\n"
   "Informe o número refente a opção de atendimento desejado:\r"
   "\n\r\n"
   "1 - Contratar nossos"
   " serviços\r\n"
   "2 - Suporte\r\n"
   "3 - Realizar pagamento"
   );


def checkMessage(message):
    return True

@bot.message_handler(func=checkMessage)
def defaultAnswer(question):
    bot.reply_to(question, default_answer)

bot.polling()