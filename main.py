import re
import os
import time
from datetime import datetime
from flask import Flask, jsonify
import tradingview as tv
from selenium.common.exceptions import InvalidSessionIdException

app = Flask(__name__)


@app.route('/<tvsymbol>/start')
def start_market(tvsymbol):
    try:
        result = tvapi.start_market_service(tvsymbol)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify({'response': result}), 200


@app.route('/<tvsymbol>/rsi')
def get_rsi(tvsymbol):
    try:
        result = tvapi.get_rsi(tvsymbol)
    except InvalidSessionIdException as e:
        return jsonify({'error': str(e)}), 501
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify({'response': result}), 200


@app.route('/<tvsymbol>/stop')
def stop_market(tvsymbol):
    try:
        result = tvapi.stop_market_service(tvsymbol)
    except InvalidSessionIdException as e:
        return jsonify({'error': str(e)}), 501
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify({'response': result}), 200


if __name__ == '__main__':
    tvapi = tv.API()
    app.run(threaded=True)
