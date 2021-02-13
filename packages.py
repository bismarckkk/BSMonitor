try:
    import ujson as json
except:
    import json
import importlib
import os
from multiprocessing import Queue
import time
from threading import Thread
import traceback


class Config:
    def __init__(self, _path=None):
        if _path is None:
            path = os.path.realpath(__file__)
            self.path = os.path.join(os.path.dirname(path), 'config')
        else:
            self.path = _path

    def getPath(self, file):
        return os.path.join(self.path, file + '.json')

    def setConfig(self, name, threadType=None, cfg=None):
        config = self.readConfig(name)
        if threadType is not None:
            config['type'] = threadType
        if cfg is not None:
            config['config'] = cfg
        with open(self.getPath(name), 'w') as file:
            json.dump(config, file)

    def readConfig(self, name):
        path = self.getPath(name)
        if os.path.exists(path):
            try:
                with open(path, 'r') as file:
                    config = json.load(file)
            except:
                config = {}
        else:
            config = {}
        return config

    def readAllConfig(self):
        files = self.readFilesName()
        configs = []
        for file in files:
            configs.append(self.readConfig(file))
        return configs

    def readFilesName(self):
        files = os.listdir(self.path)
        files.remove('example.json')
        return [it.split('.')[0] for it in files]


class Packs(Thread):
    packs = {}
    queues = {}
    names = {}
    error = {}

    def __init__(self, app):
        super().__init__(daemon=True)
        self.app = app
        path = os.path.realpath(__file__)
        self.path = os.path.dirname(path)
        self.errorQueue = Queue(maxsize=100)
        files = os.listdir(os.path.join(self.path, 'plugins'))
        files.remove('base.py')
        self.time0 = time.time()
        for file in files:
            if file[:2] == '__':
                continue
            name = file.split('.')[0]
            pub = importlib.import_module('.%s' % name, package='plugins')
            self.names[name] = pub

    def stopThread(self, name):
        if name in self.packs.keys():
            self.packs[name].terminate()
            del self.packs[name]
            if name in self.error.keys():
                del self.error[name]

    def startThread(self, name, threadType, cfg):
        if threadType not in self.names.keys():
            return False
        if name in self.packs.keys():
            self.stopThread(name)
        pack = self.names[threadType].Pub()
        queue = Queue(maxsize=500)
        self.queues[name] = queue
        pack.bind(queue, self.errorQueue, self.time0, cfg, name)
        self.packs[name] = pack
        pack.start()
        return True

    def getData(self):
        data = []
        for queue in self.queues.values():
            while not queue.empty():
                data.append(queue.get())
        return data

    def refreshErrorInfo(self):
        e = {}
        while not self.errorQueue.empty():
            info = self.errorQueue.get()
            e[info['thread']] = info['error']
            self.error[info['thread']] = info['error']
        return e

    def sendData(self):
        data = self.getData()
        if data:
            re = {}
            for d in data:
                st = d['stamp']
                for k, v in d.items():
                    if k == 'stamp' or k == 'thread':
                        continue
                    name = '%s::%s' % (d['thread'], k)
                    if name not in re.keys():
                        re[name] = [[st, v], ]
                    else:
                        re[name].append([st, v])
            self.app.emit('data', re, namespace='/ws', broadcast=True)

    def sendError(self):
        error = self.refreshErrorInfo()
        if error != {}:
            self.app.emit('error', error, namespace='/ws', broadcast=True)

    def run(self):
        while True:
            try:
                self.sendData()
                self.sendError()
                time.sleep(0.005)
            except Exception:
                print(traceback.format_exc())
