import telebot
import requests

# Substitua 'YOUR_BOT_TOKEN' pelo token do seu bot
TOKEN = 'YOUR_BOT_TOKEN'
bot = telebot.TeleBot(TOKEN)

# Função para consultar a API e obter o URL do boleto
def get_boleto_url(client_response):
    # Substitua 'API_URL' pela URL da sua API
    api_url = 'API_URL'
    # Aqui você faz a requisição à API com a resposta do cliente
    response = requests.get(f"{api_url}?query={client_response}")
    if response.status_code == 200:
        data = response.json()
        return data.get('boleto_url')
    return None

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    client_response = message.text
    boleto_url = get_boleto_url(client_response)
    
    if boleto_url:
        bot.reply_to(message, f"Aqui está o seu boleto: {boleto_url}")
    else:
        bot.reply_to(message, "Desculpe, não consegui encontrar o boleto.")

bot.polling()
