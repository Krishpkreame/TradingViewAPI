#!/bin/bash
cd /tvapi/TradingViewAPI/
git pull
pip install -r requirements.txt
sleep 1
echo ""
echo ""
echo "---------- Tradingview RSI api ----------"
echo ""
echo ""
python3 main.py