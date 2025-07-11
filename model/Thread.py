class Thread:       #进程类
    def __init__(self, pid, arrive, cpu_total, io_gap):
        self.pid = pid               #标签
        self.arrive = arrive         #到达时间
        self.cpu_total = cpu_total   # 需要cpu时间
        self.io_gap = io_gap         # io阻塞间隔时间
        self.turnaround_time = 0     # 周转时间
        self.need_cpu = cpu_total    # 剩余需要cpu时间
        self.cpu_since_io = io_gap   # 自上次io阻塞的倒计时
        self.finish_time = 0         # 上一次运行结束时间和进程结束时间
        self.queue_level = 0         # 优先级
        self.start_time = 0          # 开始运行时间
        self.state = "new"           # 状态：new, ready, running, blocked, finished
        self.time_slice = 0          # 运行后剩下时间片

    def __str__(self): #调试
        return f"{self.pid}:{self.time_slice}:{self.cpu_since_io}:{self.need_cpu}"

    def level_down(self):                #优先级减一
        self.queue_level += 1

    def time_slice_update(self, time_slice):    #更新时间片
        self.time_slice = time_slice

    def thread_new_to_run(self, time):  # 从新队列进入运行队列
        self.start_time = time
        self.state = "running"

    def thread_ready_to_run(self, time):       #从阻塞队列到就绪状态进入运行队列 或 时间片未用完再次运行
        self.state = "running"
        self.turnaround_time = time - self.arrive


    def thread_run(self, time):                # 运行
        self.turnaround_time = time + 1 - self.arrive   # 更新周转时间
        self.need_cpu -= 1              # 更新剩余需要cpu时间
        self.cpu_since_io -= 1          # 更新自上次io阻塞的倒计时
        self.time_slice -= 1              # 更新时间片

    def thread_time_slice_out(self,time):         # 时间片用完
        if self.time_slice <= 0:
            self.state = "ready"
            return True
        else:
            return False

    def queue_run_to_ready(self,time):            # 高级队列抢占
        self.state = "ready"


    def io_blocked(self,time):                   # io阻塞
        if self.cpu_since_io <= 0:
            self.cpu_since_io = self.io_gap
            self.finish_time = time + 1  #记录阻塞开始时间
            self.state = "blocked"
            return True
        else:
            return False


    def thread_blocked_to_ready(self, time):         # io阻塞结束
        if(time - self.finish_time >= 5):
            self.state = "ready"
            return True
        else:
            return False


    def if_finished(self,time):              # 进程结束
        if self.need_cpu <= 0:
            self.state = "finished"
            self.finish_time = time + 1
            self.turnaround_time = time + 1 - self.arrive
            return True
        else:
            return False





    def weight_turnaround_time(self):                   # 带权周转时间
        return self.turnaround_time / self.cpu_total

    def waiting_time(self):                            # 等待时间
        return self.turnaround_time - self.cpu_total

