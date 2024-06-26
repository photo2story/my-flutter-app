import os
import json
from flask import Flask, request, jsonify
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

app = Flask(__name__)

TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GUILD_ID = os.getenv('DISCORD_GUILD_ID')

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)

@app.route('/interactions', methods=['POST'])
def interactions():
    data = request.json

    if data['type'] == 1:
        return jsonify({
            "type": 1
        })
    
    if data['type'] == 2:
        if data['data']['name'] == 'ping':
            return jsonify({
                "type": 4,
                "data": {
                    "content": "pong"
                }
            })

    return jsonify({
        "type": 4,
        "data": {
            "content": "Unknown command"
        }
    })

@bot.event
async def on_ready():
    print(f'Bot has successfully logged in as {bot.user}')

@slash.slash(name="ping", guild_ids=[GUILD_ID])
async def _ping(ctx: SlashContext):
    await ctx.send(content="pong")

def run_bot():
    bot.run(TOKEN)

if __name__ == '__main__':
    from threading import Thread
    import nest_asyncio
    nest_asyncio.apply()

    bot_thread = Thread(target=run_bot)
    bot_thread.start()

    app.run(port=5000)



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