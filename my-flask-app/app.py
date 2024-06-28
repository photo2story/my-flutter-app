from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
CORS(app)

DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

@app.route('/send_discord_message', methods=['POST'])
def send_discord_message():
    data = request.json
    message = data.get('message')
    if message:
        payload = {
            'content': message
        }
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            return jsonify({'status': 'success'}), 200
        else:
            return jsonify({'status': 'failure', 'error': response.text}), response.status_code
    return jsonify({'status': 'failure', 'error': 'No message provided'}), 400

if __name__ == '__main__':
    app.run(debug=True)
