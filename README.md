# TradingView RSI Indicator API

A Python application for collecting RSI Indicator values in real time from TradingView using Selenium and Flask.

## Introduction

This project provides a solution for collecting market metrics, including starting and stopping market services, fetching Relative Strength Index (RSI), and more from TradingView.

## Getting Started

Follow these steps to get started with the TradingView Metrics Collector:

1. Build and run the Docker container using the provided Dockerfile.
2. Configure environment variables using `docker run` for necessary settings.
3. Use the endpoints in `app.py` to interact with TradingView metrics.

For more detailed information, refer to the specific sections in each file.

## Usage

- **Starting Market Service**: Use the `/tvsymbol/start` endpoint to start the market service for a specific TradingView symbol.

- **Fetching RSI**: Utilize the `/tvsymbol/rsi` endpoint to retrieve the Relative Strength Index (RSI) for a given symbol.

- **Stopping Market Service**: Execute a stop market order using the `/tvsymbol/stop` endpoint.

Refer to the comments in `app.py` for detailed information on each endpoint.

## Docker

The provided Dockerfile allows you to containerize the TradingView Metrics Collector. Adjust the environment variables during `docker run` for customization.

## Adding Symbols

Adding new markets to this API works very simply, just add a new entry into mongodb at `app/tvapi_info` with the template:

```json
{
  // Format EXCHANGE:SYMBOL
  "tv_symbol": "EIGHTCAP:ASX200"
}
```

- Find the TradingView symbols [here](https://www.tradingview.com/symbol).

# Enviroment Variables

Setup `DB_CONN_STR` for a mongo database you have it hosted

- Just ensure you add a user with name `user` and password `password`

Setup `SELENIUM_URL` for a Selenium Grid container you have it hosted

- Ensure there is enough shared memory and max sessions allowed

## Contributing

Contributions are welcome! Improving the code, adding your own features or remaking for differnt platform or database you be amazing to see.

Please follow the standard GitHub fork and pull request workflow.
