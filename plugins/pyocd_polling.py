from pyocd.core.helpers import ConnectHelper
from pyocd.debug.elf.symbols import ELFSymbolProvider
from pyocd.core.target import Target
from plugins.base import Base
import time
import os
import math


def i2f(f):
    exp = int((f & 2139095040) / 8388608 - 127)
    man = bin(f & 8388607)
    s = 1.
    for i in range(2, len(man)):
        s += int(man[i]) * math.pow(2, len(man) - i - 24)
    s *= math.pow(2, exp)
    if f & 2147483648:
        s *= -1
    return s


def i2d(f):
    exp = int((f & 9218868437227405312) / 4503599627370496 - 1023)
    man = bin(f & 4503599627370495)
    s = 1.
    for i in range(2, len(man)):
        s += int(man[i]) * math.pow(2, len(man) - i - 53)
    s *= math.pow(2, exp)
    if f & 0x8000000000000000:
        s *= -1
    return s


class Reader:
    def __init__(self, path):
        self.var = {}
        self.path = path
        files = os.listdir(path)
        self.project = ''
        for file in files:
            if file.split('.')[-1] == 'uvprojx':
                self.project = file.replace('.uvprojx', '')
        if self.project == '':
            raise NameError("Can't find keil project file")
        print(path)
        self.session = ConnectHelper.session_with_chosen_probe()
        print('ok')
        self.session.open()
        print('ok')
        self.board = self.session.board
        self.target = self.board.target
        self.target.elf = os.path.join(path, '%s/%s.axf' % (self.project, self.project))
        print(self.target.elf)
        self.provider = ELFSymbolProvider(self.target.elf)

    def __del__(self):
        self.session.close()

    def register(self, name, adr, cat):
        addr = self.provider.get_symbol_value(name)
        self.var[name] = {'addr': addr + int(adr), 'cat': cat}
        print('register %s ok' % name)
        print(self.var[name])

    def readVar(self, adr, cat):
        if cat == 'uint8':
            return self.target.read8(adr)
        elif cat == 'int8':
            return self.target.read8(adr) - 127
        elif cat == 'uint16':
            return self.target.read16(adr)
        elif cat == 'int16':
            return self.target.read16(adr) - 32767
        elif cat == 'float':
            return i2f(self.target.read32(adr))
        elif cat == 'double':
            return i2d(self.target.read64(adr))
        else:
            raise NameError("don't support %s" % cat)

    def readAll(self):
        re = {}
        for name, v in self.var.items():
            re[name] = self.readVar(v['addr'], v['cat'])
        return re


class Pub(Base):
    def __init__(self):
        super().__init__()
        self.fre = 0
        self.reader = None

    def init(self):
        self.fre = int(self.config['fre'])
        self.reader = Reader(self.config['path'])
        for i in range(1, 9):
            var = self.config.get('var%i' % i)
            if var == '' or var is None:
                continue
            adr = self.config['adr%i' % i]
            cat = self.config['cat%i' % i]
            self.reader.register(var, adr, cat)

    def m(self):
        p = self.reader.readAll()
        print(p)
        self.put(p)
        time.sleep(1 / self.fre)
