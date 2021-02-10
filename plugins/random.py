from plugins.base import Base
import time
import random


class Pub(Base):
    def __init__(self):
        super().__init__()

    def m(self):
        self.put({'d1': random.random()})
        print('put!')
        time.sleep(1)