class ThreadQueue:
    def __init__(self,count,array):          # 初始化队列
        self.qlists = [[] for _ in range(count)]     # 创建队列
        self.thread_time_slices = array              # 设置进程时间片

    def add_thread(self,thread):              # 添加线程到队列
        try:
            # 根据进程优先级加入相应队列
            thread.time_slice_update(self.thread_time_slices[thread.queue_level])
            self.qlists[thread.queue_level].append(thread)
        except:
            print("Error: thread queue level out of range")

    def if_empty(self):                      # 判断队列是否为空
        for i in range(len(self.qlists)):
            if len(self.qlists[i]) > 0:
                return False
        return True

    def get_thread(self):                           # 获取下一个运行的最高优先级线程
        for i in range(len(self.qlists)):
            if len(self.qlists[i]) > 0:        # 查找最高优先级不空队列
                find_thread = self.qlists[i].pop(0)
                self.qlists[i].insert(0,find_thread)
                return find_thread
        return None

    def thread_pop(self,thread):                # 从队列中移除线程
        self.qlists[thread.queue_level].remove(thread)








