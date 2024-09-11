import datetime
import sqlite3
from openpyxl import Workbook

dt = datetime.datetime.now().strftime('%Y%m%d')


def table_exists(conn, table_name):
    """
    查询数据库是否存在某名称的表
    :param conn: 创建的数据库链接
    :param table_name: 要查询的表名称
    :return:
    """
    cursor = conn.cursor()
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
    result = cursor.execute(query, (table_name,)).fetchone()
    cursor.close()
    return result is not None


def create_table(conn):
    """
    创建数据库的数据记录表
    :param conn: 创建的数据库链接
    :return:
    """
    cursor = conn.cursor()
    str1 = "Data_Rec" + dt
    str2 = "Data_Cal" + dt
    # 建表的sql语句
    sql_text_1 = '''CREATE TABLE IF NOT EXISTS {}
                   (Plugtray_Number INTEGER,
                   X REAL,
                   Y REAL);'''.format(str1, )
    sql_text_2 = '''CREATE TABLE IF NOT EXISTS {}
                       (Plugtray_Number INTEGER,
                        Single_Rate REAL,
                        Replayed_Rate REAL,
                        Missed_Rate REAL,
                        Seed_Count INTEGER,
                        Time_Consuming REAL)'''.format(str2, )

    cursor.execute(sql_text_1)
    cursor.execute(sql_text_2)
    conn.commit()
    cursor.close()


def insert_data(conn, datalist, table_class=0, is2d_sets=False):
    """
    插入数据操作
    :param conn: 创建的数据库链接
    :param datalist: 数据列表
    :param table_class: 0:Rec, 1:Cal
    :return:
    """
    cursor = conn.cursor()
    str1 = "Data_Rec" + dt
    str2 = "Data_Cal" + dt
    if table_class == 0:
        if is2d_sets:
            cursor.executemany("insert into {} values(?,?,?)".format(str1, ), datalist)
        else:
            cursor.execute("insert into {} values(?,?,?)".format(str1, ), datalist)
    elif table_class == 1:
        if is2d_sets:
            cursor.executemany("insert into {} values(?,?,?,?,?,?)".format(str2, ), datalist)
        else:
            cursor.execute("insert into {} values(?,?,?,?,?,?)".format(str2, ), datalist)
    else:
        pass
    conn.commit()
    cursor.close()


def get_max_data(conn, table_class, column_name):
    # 连接到数据库
    cursor = conn.cursor()
    str1 = "Data_Rec" + dt
    str2 = "Data_Cal" + dt
    table_name = str1 if table_class == 0 else str2

    # 构建 SQL 查询
    query = f"""
    SELECT IFNULL(MAX({column_name}), 0)
    FROM {table_name}
    """

    try:
        # 执行查询
        cursor.execute(query)

        # 获取结果
        result = cursor.fetchone()[0]

        return result

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return 0

    finally:
        # 关闭连接
        cursor.close()


def get_tables(conn):
    """
    获取数据库所有列表名
    :param conn:
    :return:
    """
    cursor = conn.cursor()
    query = "SELECT name FROM sqlite_master WHERE type='table'"
    result = cursor.execute(query).fetchall()
    namelist = []
    for r in result:
        namelist.append(r[0])
    cursor.close()
    return namelist


def get_table_row_counts(conn, table_class=0):
    cursor = conn.cursor()
    str1 = "Data_Rec" + dt
    str2 = "Data_Cal" + dt
    table_name = str1 if table_class == 0 else str2
    query = f"SELECT COUNT(*) FROM {table_name}"
    cursor.execute(query)
    result = cursor.fetchone()
    row_count = result[0]
    cursor.close()
    return row_count


def export_to_xlsx(conn, path, table_name):
    """
    将数据库中某表导出为 .xlsx
    :param conn: 创建的数据库链接
    :param path: 导出路径
    :param table_name: 要查询的表名称
    :return:
    """
    cursor = conn.cursor()
    # 获取查询结果
    selected_table = cursor.execute('select * from {}'.format(table_name))
    # 创建工作簿
    wb = Workbook()
    # 获取工作表对象
    ws = wb.active

    # 写入标题行
    if path[-11:-8] == "Cal":
        ws.append(['Plug Tray Number', "Single Rate (%)", "Replayed Rate (%)", "Missed Rate (%)", "Seed Count", "Time Consuming (s)"])
    elif path[-11:-8] == "Rec":
        ws.append(['Plug Tray Number', "X", "Y"])
    else:
        pass

    # 写入数据
    for row in selected_table:
        ws.append(row)
    # 保存文件
    wb.save(path + '.xlsx')

    cursor.close()


def get_ave_values(conn):
    """
    计算Data_Cal的列均值
    :param conn: 创建的数据库链接
    :return: [tray_number, ave_single_rate, ave_replayed_rate, ave_missed_rate]
    """
    cursor = conn.cursor()
    table_name = "Data_Cal" + dt
    results = []
    # table_name = "Data_Cal20231208"
    # SELECT AVG(aggregate_expression) FROM tables [WHERE conditions]
    sql_query = '''SELECT MAX(Plugtray_Number), 
                          AVG(Single_Rate), 
                          AVG(Replayed_Rate), 
                          AVG(Missed_Rate), 
                          AVG(Seed_Count), 
                          MAX(Time_Consuming), 
                          MIN(Time_Consuming), 
                          AVG(Time_Consuming) 
                   FROM {}'''.format(table_name, )
    try:
        rs = cursor.execute(sql_query).fetchone()
        for r in rs:
            if r is not None:
                results.append(round(r, 2))
                # print(r)
        return results

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []

    finally:
        # 关闭连接
        cursor.close()
