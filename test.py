from plugins.pyocd_polling import Pub
import ujson

p = Pub()
p.config = ujson.load(open('config/042.json', 'r'))['config']
p.start()
p.join()