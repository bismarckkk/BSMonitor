from threading import Thread
import time
try:
    import ujson as json
except ImportError:
    import json
import traceback
from multiprocessing import Process


class Base(Process):
    queue = None
    errorQueue = None
    time0 = 0
    path = ''
    stop = False

    def __init__(self):
        super().__init__(daemon=True)

    def bind(self, q, e, time0, cfg, name):
        self.queue = q
        self.errorQueue = e
        self.time0 = time0
        self.config = cfg
        self.name = name

    def init(self):
        pass

    def run(self):
        try:
            self.init()
        except Exception:
            self.errorQueue.put({'thread': self.name, 'error': traceback.format_exc()})
            self.stop = True
        while not self.stop:
            try:
                self.m()
            except Exception:
                self.errorQueue.put({'thread': self.name, 'error': traceback.format_exc()})
                break
        self.stop = True

    def getStamp(self):
        return time.time() - self.time0

    def put(self, data):
        self.queue.put({
            'thread': self.name,
            'stamp': self.getStamp(),
            **data
        })

    def m(self):
        pass
