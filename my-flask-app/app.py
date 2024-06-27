import os
import discord
import asyncio
from flask import Flask, request
from dotenv import load_dotenv
from threading import Thread

# 필요한 라이브러리 추가
import logging
logging.basicConfig(level=logging.DEBUG)

load_dotenv()

app = Flask(__name__)

TOKEN = os.getenv('DISCORD_BOT_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    logging.info(f'Bot has logged in as {bot.user.name}')
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send('Bot has logged in successfully!')
        logging.info(f'Message sent to channel: {CHANNEL_ID}')
    else:
        logging.error(f'Channel not found: {CHANNEL_ID}')

@app.route('/execute_discord_command', methods=['POST'])
def execute_discord_command():
    data = request.json
    logging.debug(f"Received data: {data}")

    async def send_message():
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(data['message'])
            logging.info(f"Message sent to Discord: {data['message']}")
        else:
            logging.error(f"Channel not found: {CHANNEL_ID}")

    asyncio.run_coroutine_threadsafe(send_message(), bot.loop)
    return 'Message sent', 200

def run_discord_bot():
    bot.run(TOKEN)

if __name__ == '__main__':
    Thread(target=run_discord_bot).start()
    app.run(host='0.0.0.0', port=5000)


"""
flutter run -d chrome

.\.venv\Scripts\activate
cd..
cd my-flutter-app/my-flask-app
python app.py 

npm run build
heroku login
git init
heroku git:remote -a he-react-app

git commit -m "react build"
git push heroku main
"""