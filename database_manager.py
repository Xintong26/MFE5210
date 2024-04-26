import pandas as pd
import os
import sqlite3

directory_path = 'E:/2023Spring/Algorithmic Trading/database'


# 单条数据更新（模拟每分钟获取新一分钟的数据）
def save_market_records(new_min_data, table_name, database, if_exists_action='append'):
    conn = sqlite3.connect(directory_path + '/' + str(database) + '.db')
    row_data = pd.DataFrame([new_min_data])
    try:
        row_data.to_sql(str(table_name), conn, if_exists=if_exists_action, index=False)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

# 数据表格存储
def data_save(dataframe, table_name, database, if_exists_action='replace'):
    conn = sqlite3.connect(directory_path + '/' + str(database) + '.db')
    try:
        dataframe.reset_index().to_sql(str(table_name), conn, if_exists=if_exists_action, index=False)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()


# 数据表格读取
def data_read(table_name, database):
    conn = sqlite3.connect(directory_path + '/' + str(database) + '.db')

    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        df.set_index('datetime', inplace=True)
        df.index = pd.to_datetime(df.index)
    except Exception as e:
        print(f"Error reading table {table_name}: {e}")
        return None
    finally:
        # 关闭数据库连接
        conn.close()

    return df


def find_sqlite_databases(directory_path):
    return [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith('.db')]


def get_table_date_ranges(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    table_info = []
    for (table_name,) in tables:
        # 尝试查询每个表的日期范围
        try:
            cursor.execute(f"SELECT MIN(datetime), MAX(datetime) FROM {table_name}")
            min_datetime, max_datetime = cursor.fetchone()
            datetime_range = f"{min_datetime} to {max_datetime}"
        except sqlite3.OperationalError:  # 如果日期列不存在或其他错误
            datetime_range = "Date column not found or error"

        table_info.append({
            'table_name': table_name,
            'datetime_range': datetime_range
        })

    conn.close()
    return table_info