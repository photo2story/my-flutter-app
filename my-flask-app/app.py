from flask import Flask, request, jsonify
from flask_cors import CORS
from estimate_stock import estimate_stock  # 주식 데이터를 처리하는 모듈을 가져옵니다.

app = Flask(__name__)
CORS(app)

@app.route('/api/estimate_stock', methods=['POST'])
def estimate_stock_route():
    data = request.json
    stock_name = data.get('stock_name')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    # 주식 데이터를 처리하고 결과를 반환합니다.
    result = estimate_stock(stock_name, start_date, end_date)
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
