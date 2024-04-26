import ccxt
import backtester as btest

exchange_id = 'binance'
api_key = 'your_api_key'
api_secret = 'your_api_secret'

# 初始化交易所对象
exchange = getattr(ccxt, exchange_id)({
    'apiKey': api_key,
    'secret': api_secret,
})


def execute_trade(trade_data, position_data):
    signal = btest.return_calculation(trade_data, position_data)
    symbol = 'BTC'
    amount = 1

    if signal == 1:
        print("Sending buy order")
        order = exchange.create_market_buy_order(symbol, amount)
        print(order)

    elif signal == -1:
        print("Sending sell order")
        order = exchange.create_market_sell_order(symbol, amount)
        print(order)

    else:
        print("No trading")