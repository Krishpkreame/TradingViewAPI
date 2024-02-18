from flask import Flask, jsonify  # For HTTP API
import tradingview as tv  # For TradingView API

app = Flask(__name__)  # Initialize Flask app

tvapi = tv.API()  # Initialize TradingView API


# API start point for each market
@app.route('/<tvsymbol>/start')
def start_market(tvsymbol):
    """
    Starts the market service for the specified symbol.

    Parameters:
    tvsymbol (str): The symbol for which the market service needs to be started.

    Returns:
    dict: A dictionary containing the response message.

    Raises:
    Exception: If the market service fails to start.
    """
    try:
        # Start market service for symbol
        result = tvapi.start_market_service(tvsymbol)
    except Exception as e:
        # Return error message if market didn't start
        return jsonify({'error': str(e)}), 500
    # Return success message if market started
    return jsonify({'response': result}), 200


# API rsi point for each market
@app.route('/<tvsymbol>/rsi')
def get_rsi(tvsymbol):
    """
    Get the RSI (Relative Strength Index) value for a given symbol.

    Parameters:
    tvsymbol (str): The symbol for which to retrieve the RSI value.

    Returns:
    dict: A JSON response containing the RSI value.

    Raises:
    InvalidSessionIdException: If the session ID is invalid or expired.
    Exception: If the RSI value is not found or an error occurs.

    """
    try:
        # Get rsi value for symbol
        result = tvapi.get_rsi(tvsymbol)
    except InvalidSessionIdException as e:
        # Return error message if session is timed out - flags doesn't match session
        return jsonify({'error': str(e)}), 501
    except Exception as e:
        # Return error message if rsi value not found (e.g. market not started)
        return jsonify({'error': str(e)}), 500
    # Return rsi json found
    return jsonify({'response': result}), 200


# API stop point for each market
@app.route('/<tvsymbol>/stop')
def stop_market(tvsymbol):
    """
    Stop the market service for a given symbol.

    Parameters:
    tvsymbol (str): The symbol for which the market service needs to be stopped.

    Returns:
    dict: A dictionary containing the response message.

    Raises:
    InvalidSessionIdException: If the session is timed out and the flags do not match the session.
    Exception: If the RSI value is not found (e.g., market not started).

    """
    try:
        # Stop market service for symbol
        result = tvapi.stop_market_service(tvsymbol)
    except InvalidSessionIdException as e:
        # Return error message if session is timed out - flags doesn't match session
        return jsonify({'error': str(e)}), 501
    except Exception as e:
        # Return error message if RSI value not found (e.g., market not started)
        return jsonify({'error': str(e)}), 500
    # Return success message if market stopped
    return jsonify({'response': result}), 200
