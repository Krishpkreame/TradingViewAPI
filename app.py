from flask import Flask, jsonify
import tradingview as tv

app = Flask(__name__)

tvapi = tv.API()


@app.route('/<tvsymbol>/start')
def start_market(tvsymbol):
    """
    Starts the market service for the specified TradingView symbol.

    Parameters:
    tvsymbol (str): The TradingView symbol to start the market service for.

    Returns:
    tuple: A tuple containing the JSON response and the HTTP status code. The JSON response contains the result of starting the market service.

    Example:
    start_market("AAPL")
    """
    result = tvapi.start_market_service(tvsymbol)
    if result["success"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@app.route('/<tvsymbol>/rsi')
def get_rsi(tvsymbol):
    """
    Get the Relative Strength Index (RSI) for a given TradingView symbol.

    Parameters:
    tvsymbol (str): The symbol for which to retrieve the RSI.

    Returns:
    tuple: A tuple containing the JSON response and the HTTP status code.
    """
    result = tvapi.get_rsi(tvsymbol)
    if result["success"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@app.route('/<tvsymbol>/stop')
def stop_market(tvsymbol):
    """
    Executes a stop market order for the specified trading symbol.

    Parameters:
    tvsymbol (str): The trading symbol for which the stop market order is to be executed.

    Returns:
    tuple: A tuple containing the JSON response and the HTTP status code. The JSON response contains the result of the stop market order execution, while the HTTP status code indicates the success or failure of the request.
    """
    result = tvapi.stop_market_service(tvsymbol)
    if result["success"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 400
