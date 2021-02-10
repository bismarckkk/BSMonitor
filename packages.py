try:
    import ujson as json
except:
    import json
import importlib
import os
from queue import Queue
import time


class Packs:
    packs = {}
    queues = []
    data = []
    names = {}

    def __init__(self):
        path = os.path.realpath(__file__)
        self.path = os.path.dirname(path)
        self.errorQueue = Queue(maxsize=100)
        files = os.listdir('./plugins')
        files.remove('base.py')
        self.time0 = time.time()
        for file in files:
            if file[:2] == '__':
                continue
            name = file.split('.')[0]
            pub = importlib.import_module('.%s' % name, package='plugins')
            self.names[name] = pub

    def start(self, name, cfg):
        if name not in self.names.keys():
            return
        if name in self.packs.keys():
            del self.packs[name]
        pack = self.names[name].Pub()
        queue = Queue(maxsize=500)
        self.queues.append(queue)
        path = os.path.join(self.path, cfg + '.json')
        pack.bind(queue, self.errorQueue, self.time0, path)
        self.packs[name] = pack
        pack.start()

    def refreshData(self):
        for queue in self.queues:
            while not queue.empty():
                self.data.append(queue.get())
                print('get!')

    def getErrorInfo(self):
        errors = []
        while not self.errorQueue.empty():
            errors.append(self.errorQueue.get())
        return errors

    def getData(self, stamp):
        re = {}
        if stamp is not None:
            data = filter(lambda x: x['stamp'] > stamp, self.data)
        else:
            data = self.data
        for d in data:
            st = d['stamp']
            for k, v in d.items():
                if k == 'stamp':
                    continue
                if k not in re.keys():
                    re[k] = [[st, v]]
                else:
                    re[k].append([st, v])
        return re
