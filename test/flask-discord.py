# flask-discord.py    
import os
import asyncio
import threading
import requests
import certifi
import discord
from discord.ext import commands
from flask import Flask, redirect, url_for, render_template, request, jsonify
from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
from dotenv import load_dotenv
from datetime import datetime

os.environ['SSL_CERT_FILE'] = certifi.where()
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.config["DISCORD_CLIENT_ID"] = os.getenv("DISCORD_CLIENT_ID")
app.config["DISCORD_CLIENT_SECRET"] = os.getenv("DISCORD_CLIENT_SECRET")
app.config["DISCORD_REDIRECT_URI"] = os.getenv("DISCORD_REDIRECT_URI")
app.config["DISCORD_BOT_TOKEN"] = os.getenv("DISCORD_BOT_TOKEN")

discord_oauth = DiscordOAuth2Session(app)

TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='', intents=intents)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login/')
def login():
    return discord_oauth.create_session()

@app.route('/callback/')
def callback():
    discord_oauth.callback()
    user = discord_oauth.fetch_user()
    welcome_user(user)
    return redirect(url_for(".me"))

@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    return redirect(url_for("login"))

@app.route("/me/")
@requires_authorization
def me():
    user = discord_oauth.fetch_user()
    return f"""
    <html>
        <head>
            <title>{user.name}</title>
        </head>
        <body>
            <img src='{user.avatar_url}' />
        </body>
    </html>"""

def welcome_user(user):
    dm_channel = discord_oauth.bot_request("/users/@me/channels", "POST", json={"recipient_id": user.id})
    discord_oauth.bot_request(
        f"/channels/{dm_channel['id']}/messages", "POST", json={"content": "Thanks for authorizing the app!"}
    )

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(f'Bot has successfully logged in: {bot.user.name}')
    else:
        print(f'Failed to get channel with ID {CHANNEL_ID}')

@bot.command()
async def ping(ctx):
    await ctx.send(f'pong: {bot.user.name}')

if __name__ == "__main__":
    async def run_bot():
        await bot.start(TOKEN)
    
    def run_flask():
        app.run(debug=True, use_reloader=False)

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_bot())

#  .\.venv\Scripts\activate
# python flask-discord.py    