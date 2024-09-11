import sqlite3
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
from Scripts import sqlite_unit
import queue
import threading
from concurrent.futures import ThreadPoolExecutor
import numpy as np

lock = threading.Lock()
def func(n, i):
    # lock.acquire()
    time.sleep(i)
    print(f"func:{i}")
    # lock.release()


def func1(n):
    # lock.acquire()
    time.sleep(n)
    print(f"func1:{n}")
    # lock.release()


def multipool():
    with ThreadPoolExecutor(max_workers=4) as executor:
        # executor.map(func, range(2))
        all_tasks = [executor.submit(func, i, 2) for i in range(5)]
        # for future in all_tasks:
        #     print(future.running())
        for future in as_completed(all_tasks):
            data = future.result()
        futures2 = executor.submit(func1, 1)
        print(2)



def pyqt_test():
    # 创建数据库链接
    conn = sqlite3.connect('test.db')
    sqlite_unit.create_table(conn)
    rc = sqlite_unit.get_table_row_counts(conn, 1)
    for i in range(10):
        # list = []
        sn = rc + i + 1
        sr = round(random.uniform(90, 98), 2)
        rr = round(random.uniform(2, 6), 2)
        mr = round(random.uniform(3, 5), 2)
        tc = round(random.uniform(2, 4), 2)
        # list.append([sn, sr, rr, mr, tc])
        sqlite_unit.insert_data(conn, [[sn, sr, rr, mr, tc], [sn, sr, rr, mr, tc]], 1, True)


# 定义处理函数
def process_number(q):
    while True:
        try:
            # 非阻塞式获取队列中的数据
            number = q.get(block=False)
            if number % 3 == 0:
                print(f"{number} is divisible by 3")
            else:
                print(f"{number} is not divisible by 3")
            # 标记任务完成
            q.task_done()
        except queue.Empty:
            # 如果队列为空，退出循环
            break


# 定义处理函数
def process_row(q):
    while True:
        try:
            # 非阻塞式获取队列中的数据
            row = q.get(block=False)
            row_sum = np.sum(row)
            print(f"Row {list(row)}: sum = {row_sum}")
            # 标记任务完成
            q.task_done()
        except queue.Empty:
            # 如果队列为空，退出循环
            break


if __name__ == '__main__':
    # pyqt_test()
    # 创建一个队列

    # data_queue = queue.Queue()
    #
    # # 填充队列with数字1到100
    # for i in range(1, 101):
    #     data_queue.put(i)
    #
    # with ThreadPoolExecutor(max_workers=4) as executor:
    #     # 提交4个任务给线程池
    #     for _ in range(6):
    #         executor.submit(process_number, data_queue)
    #
    # # 等待所有任务完成
    # data_queue.join()

    # 创建一个8x4的2维数组
    data_array = np.random.randint(1, 100, size=(8, 4))
    print("Original array:")
    print(data_array / 100)

    # 创建一个队列
    data_queue = queue.Queue()

    slice_array = data_array[:, :2]

    # 将数组的每一行放入队列
    for row in slice_array:
        data_queue.put([row[0] / 100, row[1] / 1000])

        # 创建一个包含4个线程的线程池
    with ThreadPoolExecutor(max_workers=4) as executor:
        # 提交4个任务给线程池
        for _ in range(4):
            executor.submit(process_row, data_queue)

        # 等待所有任务完成
    data_queue.join()






