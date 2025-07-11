import random
import json
from model.Thread import Thread
def thread_random_create(num):                                    # 随机生成线程
    threads = []
    for i in range(num):
        pid = i + 1
        arrive = random.randint(0, 100)
        cpu_total = random.randint(10, 50)
        io_gap = random.randint(0, cpu_total)
        threads.append(Thread(pid, arrive, cpu_total, io_gap))
    return threads

def thread_json_read():                                            # 从json文件中读取线程
    with open("sample.json", 'r') as f:
        threads_json = json.load(f)

    threads = [
        Thread(
            thread["pid"],
            thread["arrive"],
            thread["cpu_total"],
            thread["io_gap"]
        )
        for thread in threads_json
    ]
    return threads
