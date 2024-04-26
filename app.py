import tkinter as tk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import database_manager as dbm
import trading_strategy as ts
import backtester as btest
import os

data = pd.read_csv(r"E:\2023Spring\Algorithmic Trading\data\crypto_full_1min\BTC_full_1min.txt",
                   names=['datetime', 'open', 'high', 'low', 'close', 'volume'],
                   parse_dates=['datetime']).sort_values('datetime').set_index('datetime')

data_history = data['2022-12-25':'2022']
data_future = data['2023':].reset_index()
dbm.data_save(data_history, 'BTC', 'crypto_1min')

last_index_processed = 0


def fetch_and_process_data(market_data, table_name, database, short, long):
    global last_index_processed
    # 只处理新数据
    new_data = market_data.iloc[last_index_processed:]
    last_index_processed = last_index_processed+1  # 更新处理的位置

    for i in range(len(market_data)):
        min_data_updated = new_data.iloc[i]
        dbm.save_market_records(min_data_updated, table_name, database)
        data_used = dbm.data_read(table_name, database)
        strategy_data = ts.moving_average_crossover_strategy(data_used, short, long)
        return_data = btest.return_calculation(data_used, strategy_data)[0]
        dbm.data_save(return_data, 'return', 'backtester')
        positions = btest.return_calculation(data_used, strategy_data)[1]
        cost = btest.trading_cost(strategy_data)
        return return_data, positions, cost


def update_gui(position_label, pnl_label, sharpe_label, drawdown_label, cost_label, canvas, ax, market_data, table_name, database,
               text_widget, directory_path,short, long):
    data = fetch_and_process_data(market_data, table_name, database, short, long)[0]
    pos = fetch_and_process_data(market_data, table_name, database, short, long)[1].iloc[-1]
    data_cumsum = data.cumsum()

    # 更新PnL
    ax.clear()
    ax.plot(data_cumsum.index.values, data_cumsum.values)
    ax.set_title("Gross PnL")
    ax.set_xlabel("Time")
    ax.set_ylabel("PnL")
    canvas.draw()

    # 计算指标
    sharpe_ratio = btest.sharp_ratio(data)
    max_drawdown = btest.maximum_drawdown(data)

    trading_cost = fetch_and_process_data(market_data, table_name, database, short, long)[2]

    # 更新标签
    pnl_label.config(text=f"最新数据: 已更新")
    position_label.config(text=f"仓位：{pos}")
    sharpe_label.config(text=f"夏普比率: {sharpe_ratio:.2f}")
    drawdown_label.config(text=f"最大回撤: {max_drawdown:.2%}")
    cost_label.config(text=f"累计交易成本：{trading_cost:.4f}")


    load_database_info(text_widget, directory_path)

    # 5秒后再次调用此函数
    drawdown_label.after(10000, update_gui, position_label, pnl_label, sharpe_label, drawdown_label, cost_label, canvas, ax, market_data,
                    table_name, database, text_widget, directory_path, short, long)

def load_database_info(text_widget, directory_path):
    text_widget.delete('1.0', tk.END)  # 清空文本框
    databases = dbm.find_sqlite_databases(directory_path)
    for db_path in databases:
        table_info = dbm.get_table_date_ranges(db_path)
        text_widget.insert(tk.END, f"Database: {os.path.basename(db_path)}\n")
        for info in table_info:
            text_widget.insert(tk.END, f"Table: {info['table_name']}, Date Range: {info['datetime_range']}\n")




def create_app(market_data, table_name, database, directory_path, short, long):
    root = tk.Tk()
    root.title("数据监控仪表板")

    # 设置绘图区域
    fig, ax = plt.subplots()
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # 设置状态和指标标签
    position_label = ttk.Label(root, text="仓位: 计算中...")
    position_label.pack(side=tk.TOP, fill=tk.X)
    pnl_label = ttk.Label(root, text="等待数据...")
    pnl_label.pack(side=tk.TOP, fill=tk.X)
    sharpe_label = ttk.Label(root, text="夏普比率: 计算中...")
    sharpe_label.pack(side=tk.TOP, fill=tk.X)
    drawdown_label = ttk.Label(root, text="最大回撤: 计算中...")
    drawdown_label.pack(side=tk.TOP, fill=tk.X)
    cost_label = ttk.Label(root, text="累计交易成本: 计算中...")
    cost_label.pack(side=tk.TOP, fill=tk.X)


    text_widget = tk.Text(root, height=10)
    text_widget.pack(pady=20, padx=20)

    load_button = ttk.Button(root, text="Load Database Info")
    load_button.pack(pady=10)

    # 启动GUI更新循环
    update_gui(position_label, pnl_label, sharpe_label, drawdown_label, cost_label, canvas, ax, market_data, table_name, database, text_widget, directory_path, short, long)

    return root

if __name__ == "__main__":
    directory_path = 'E:/2023Spring/Algorithmic Trading/database'
    app = create_app(data_future, 'BTC', 'crypto_1min', directory_path, short=10, long=20)
    app.mainloop()