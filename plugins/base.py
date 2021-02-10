from threading import Thread
import time
try:
    import ujson as json
except ImportError:
    import json
import traceback


class Base(Thread):
    queue = None
    errorQueue = None
    time0 = 0
    path = ''

    def __init__(self):
        super().__init__(daemon=True)
        print('Init!')

    def bind(self, q, e, time0, path):
        self.queue = q
        self.errorQueue = e
        self.time0 = time0
        self.path = path
        print('bind')

    def run(self):
        while True:
            try:
                self.m()
            except Exception:
                self.errorQueue.put(traceback.format_exc())
                break

    def getStamp(self):
        return time.time() - self.time0

    def put(self, data):
        self.queue.put({
            'stamp': self.getStamp(),
            **data
        })

    def getConfig(self):
        with open(self.path, 'r') as file:
            return json.load(file)

    def m(self):
        pass
