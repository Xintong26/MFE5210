import numpy as np
import pandas as pd

def moving_average_crossover_strategy(data, short_window, long_window):

    data_strategy = pd.DataFrame()
    # 计算短期和长期移动平均线
    data_strategy['short_ma'] = data['close'].rolling(window=str(short_window)+'min', min_periods=short_window).mean()
    data_strategy['long_ma'] = data['close'].rolling(window=str(long_window)+'min', min_periods=short_window).mean()

    # 创建信号列
    data_strategy['signal'] = 0
    # 短期线下穿长期线为买入信号
    data_strategy['signal'] = np.where(data_strategy['short_ma'] < data_strategy['long_ma'], 1, 0)
    # 计算持仓
    data_strategy['positions'] = data_strategy['signal']
    # 计算持仓变化
    data_strategy['positions_change'] = data_strategy['signal'].diff()

    return data_strategy