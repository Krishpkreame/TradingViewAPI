from flask import Flask, jsonify  # For HTTP API
import tradingview as tv  # For TradingView API
from selenium.common.exceptions import InvalidSessionIdException  # For Selenium Error

app = Flask(__name__)  # Initialize Flask app

tvapi = tv.API()  # Initialize TradingView API


# API start point for each market
@app.route('/<tvsymbol>/start')
def start_market(tvsymbol):
    try:
        # Start market service for symboll
        result = tvapi.start_market_service(tvsymbol)
    except Exception as e:
        # Return error message if market didnt start
        return jsonify({'error': str(e)}), 500
    # Return success message if market started
    return jsonify({'response': result}), 200


# API rsi point for each market
@app.route('/<tvsymbol>/rsi')
def get_rsi(tvsymbol):
    try:
        # Get rsi value for symbol
        result = tvapi.get_rsi(tvsymbol)
    except InvalidSessionIdException as e:
        # Return error message if session is timed out  - flags doesnt match session
        return jsonify({'error': str(e)}), 501
    except Exception as e:
        # Return error message if rsi value not found (eg . market not started)
        return jsonify({'error': str(e)}), 500
    # Return rsi json found
    return jsonify({'response': result}), 200


# API stop point for each market
@app.route('/<tvsymbol>/stop')
def stop_market(tvsymbol):
    try:
        # Stop market service for symbol
        result = tvapi.stop_market_service(tvsymbol)
    except InvalidSessionIdException as e:
        # Return error message if session is timed out  - flags doesnt match session
        return jsonify({'error': str(e)}), 501
    except Exception as e:
        # Return error message if rsi value not found (eg . market not started)
        return jsonify({'error': str(e)}), 500
    # Return success message if market stopped
    return jsonify({'response': result}), 200
