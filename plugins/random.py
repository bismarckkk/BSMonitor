from plugins.base import Base
import time
import random


class Pub(Base):
    def __init__(self):
        super().__init__()
        self.fre = 0

    def init(self):
        self.fre = int(self.config['fre'])

    def m(self):
        self.put({'d1': random.random()})
        time.sleep(1 / self.fre)
