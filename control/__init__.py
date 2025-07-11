import sys

from model.ThreadQueue import ThreadQueue

body = ThreadQueue(3,[2,4,sys.maxsize])  # 创建线程队列