import os
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask, request, jsonify
import asyncio

app = Flask(__name__)

TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot has logged in as {bot.user}')
    try:
        await bot.tree.sync()
        print('Synced commands successfully.')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

@app.route('/execute_discord_command', methods=['POST'])
def execute_discord_command():
    data = request.get_json()
    command = data.get('command')

    if command == '/ping':
        asyncio.run_coroutine_threadsafe(send_ping_command(), bot.loop)
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'invalid command'}), 400

async def send_ping_command():
    channel = bot.get_channel(int(CHANNEL_ID))
    if channel:
        await channel.send('/ping')
    else:
        print(f"Channel not found: {CHANNEL_ID}")

@bot.tree.command(name="ping", description="Responds with pong")
async def ping_command(interaction: discord.Interaction):
    await interaction.response.send_message("pong")

async def run_discord_bot():
    async with bot:
        await bot.start(TOKEN)

def start_flask_app():
    app.run(debug=False, host='0.0.0.0')

if __name__ == '__main__':
    asyncio.run(run_discord_bot())
    start_flask_app()

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