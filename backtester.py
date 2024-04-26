import numpy as np

def return_calculation(trade_data, position_data):

    positions = position_data['positions']
    return_rate = trade_data['close'].pct_change()
    strategy_return = return_rate*positions.shift(1)

    return strategy_return, positions


def sharp_ratio(data):

    ret_gross = data.mean()*24*60
    std_gross = np.std(data)*np.sqrt(24*60)
    sharp_ratio_gross = ret_gross/std_gross

    return sharp_ratio_gross

def maximum_drawdown(data):
    return -(data.cumsum() - data.cumsum().cummax()).min()


def trading_cost(position_data):
    positions_change = position_data['positions'].diff()
    cost = (abs(positions_change)*0.0003).sum()
    return cost