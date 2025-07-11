from control import body
from control.Thread_input import *
threads = []     # 进程列表
current_time = 0                   # 当前时间
current_thread = None               # 当前运行的进程
next_thread = None                  # 下一个运行的进程
cpu_busy = False                    # cpu是否被占用
gantt_chart = []                    # 进程运行时间表
performance_metrics = {
    "total_turnaround_time": 0,
    "total_weighted_turnaround_time": 0,
    "total_waiting_time": 0,
    "cpu_utilization": 0,
    "throughput": 0,
}# 性能指标

def time_proceed():   # 模拟时间流逝
    global current_time, current_thread, cpu_busy, next_thread    # 全局变量

    #检查是否有新队列到达
    for thread in threads:
        if thread.arrive == current_time:
            body.add_thread(thread)

    #检查完成阻塞进程将其加入到队列
    for thread in threads:
        if thread.state == "blocked" and thread.thread_blocked_to_ready(current_time):
            thread.time_slice_update(body.thread_time_slices[thread.queue_level])
            body.add_thread(thread)

    #获取当前优先级最高进程
    next_thread = body.get_thread()

    if next_thread and current_thread is None:    # 当前没有进程运行
        current_thread = next_thread
        if current_thread.state == "new":                 # 进程刚创建
            current_thread.thread_new_to_run(current_time)
        elif current_thread.state == "ready":            # 进程刚进入就绪队列
            current_thread.thread_ready_to_run(current_time)
    elif next_thread and current_thread:    # 当前有进程运行，但不是最高优先级
        if next_thread != current_thread:
            current_thread.queue_run_to_ready(current_time)   # 当前进程保留时间片，被抢占，进入就绪队列
            current_thread = next_thread
            if current_thread.state == "new":             #同上
                current_thread.thread_new_to_run(current_time)
            elif current_thread.state == "ready":
                current_thread.thread_ready_to_run(current_time)

                
    if current_thread:        # 当前有进程占用cpu
        current_thread.thread_run(current_time)
        if current_thread.if_finished(current_time):
            body.thread_pop(current_thread)
            gantt_chart.append((current_thread.pid, current_time, 0))  #加入甘特图，代表进程结束
            current_thread = None
        elif current_thread.io_blocked(current_time):  #阻塞
            body.thread_pop(current_thread)
            gantt_chart.append((current_thread.pid, current_time, 1))  #加入甘特图，代表进程阻塞
            current_thread = None
        elif current_thread.thread_time_slice_out(current_time):  #时间片用完
            gantt_chart.append((current_thread.pid, current_time, 2))  #加入甘特图，代表进程时间片用完
            body.thread_pop(current_thread)
            current_thread.level_down()   #降级
            body.add_thread(current_thread)
            current_thread = None
        else:
            gantt_chart.append((current_thread.pid, current_time, 3)) #加入甘特图，代表进程接着运行
    else:  # 当前没有进程占用cpu
        gantt_chart.append((0, current_time, 4))  # 加入甘特图，代表无进程运行
    current_time += 1


def calculate_performance_metrics():        # 计算性能指标
    global performance_metrics
    completed_threads = [thread for thread in threads if thread.state == "finished"]

    for thread in completed_threads:
        performance_metrics["total_turnaround_time"] += thread.turnaround_time
        performance_metrics["total_weighted_turnaround_time"] += thread.weight_turnaround_time()
        performance_metrics["total_waiting_time"] += thread.waiting_time()

    performance_metrics["average_turnaround_time"] = (
            performance_metrics["total_turnaround_time"] / len(completed_threads))
    performance_metrics["average_weighted_turnaround_time"] = (
            performance_metrics["total_weighted_turnaround_time"] / len(completed_threads))
    performance_metrics["average_waiting_time"] = (
            performance_metrics["total_waiting_time"] / len(completed_threads))

    cpu_busy_time = sum([thread.cpu_total for thread in completed_threads])
    performance_metrics["cpu_utilization"] = cpu_busy_time / current_time

    performance_metrics["throughput"] = len(completed_threads) / current_time

    return performance_metrics

def main_process():                 # 主进程
    global threads
    print("开始模拟进程调度")
    print("请选择输入方式：(1。随机生成/2.json文件读取)")
    while True:
        choice = input()
        if choice == "1":
            num = int(input("请输入进程数量："))
            threads = thread_random_create(num)
            break
        elif choice == "2":
            threads = thread_json_read()
            break
        else:
            print("请重新输入")


    while any(thread.state != "finished" for thread in threads):# 判断是否所有进程都完成
        time_proceed()                 # 模拟时间流逝

    performance_metrics = calculate_performance_metrics()          # 计算性能指标

    for process in gantt_chart:              # 打印甘特图
        print((f"{process[1]}-{process[1]+1}:PID{process[0]}"
               if process[2]!=4 else f"{process[1]}-{process[1]+1}:None")
              +("(finished)"if process[2]==0
                else "(blocked)" if process[2]==1
                else "(time slice out)" if process[2]==2
                else "(running)" if process[2]==3
                else "")
               )

    for thread in threads:                 # 打印进程信息
        turnaround = thread.turnaround_time
        weighted = thread.weight_turnaround_time()
        waiting = thread.waiting_time()
        finish_time = thread.finish_time
        arrive = thread.arrive
        print(f"PID {thread.pid} 到达{arrive}ms  完成{finish_time}ms  周转{turnaround}  带权{weighted:.2f}  等待{waiting}")

    print(f"\n平均周转时间: {performance_metrics['average_turnaround_time']:.2f} ms")
    print(f"CPU利用率: {performance_metrics['cpu_utilization']:.2f}")
    print(f"吞吐量: {performance_metrics['throughput']:.2f} 进程/ms")

