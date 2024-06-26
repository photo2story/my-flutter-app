import os
import discord
from discord.ext import commands
from discord import app_commands
import nest_asyncio
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# nest_asyncio 적용
nest_asyncio.apply()

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

app = Flask(__name__)
CORS(app)

@tree.command(name="ping", description="Responds with pong")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("pong")

@client.event
async def on_ready():
    await tree.sync()
    print(f'Logged in as {client.user}')

@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/execute_discord_command', methods=['POST'])
def execute_discord_command():
    data = request.json
    asyncio.run_coroutine_threadsafe(send_ping_command(), client.loop)
    return jsonify({'success': True})

async def send_ping_command():
    channel = client.get_channel(int(os.getenv('DISCORD_CHANNEL_ID')))
    if channel:
        await channel.send('ping')
    else:
        print(f"Channel not found: {os.getenv('DISCORD_CHANNEL_ID')}")

def run_discord_bot():
    client.run(os.getenv('DISCORD_APPLICATION_TOKEN'))

if __name__ == '__main__':
    run_discord_bot()
    app.run()



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