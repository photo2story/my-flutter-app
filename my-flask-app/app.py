import os
import json
from flask import Flask, request, jsonify
from discord_interactions import verify_key_decorator, InteractionType, InteractionResponseType

app = Flask(__name__)

PUBLIC_KEY = os.getenv('DISCORD_PUBLIC_KEY')

@app.route('/interactions', methods=['POST'])
@verify_key_decorator(PUBLIC_KEY)
def interactions():
    data = request.json

    if data['type'] == InteractionType.PING:
        return jsonify({
            "type": InteractionResponseType.PONG
        })
    
    if data['type'] == InteractionType.APPLICATION_COMMAND:
        if data['data']['name'] == 'ping':
            return jsonify({
                "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
                "data": {
                    "content": "pong"
                }
            })

    return jsonify({
        "type": InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
        "data": {
            "content": "Unknown command"
        }
    })

if __name__ == '__main__':
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