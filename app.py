from flask import Flask, render_template, request
import socket
from gevent.pywsgi import WSGIServer
import webbrowser
import qrcode
import packages
try:
    import ujson as json
except:
    import json

app = Flask(__name__)
packs = packages.Packs()


@app.route('/')
def hello_world():
    return render_template('base.html')


@app.route('/chart')
def chart():
    return render_template('chart.html')


@app.route('/list')
def rlist():
    return render_template('list.html')


@app.route('/getNewData')
def getNewData():
    st = float(request.args.get('stamp'))
    packs.refreshData()
    return json.dumps(packs.getData(st))


@app.errorhandler(404)
def error404(_):
    return render_template('404.html'), 404


@app.errorhandler(500)
def error500(_):
    return render_template('500.html'), 500


if __name__ == '__main__':
    cname = socket.getfqdn(socket.gethostname())
    ip = socket.gethostbyname(cname)
    port = 8880
    url = 'http://%s:%i' % (ip, port)
    img = qrcode.make(url, border=5)
    img.save('./static/qrcode.jpg')

    # server = WSGIServer(('127.0.0.1', 8880), app)
    # webbrowser.open(url)
    # server.serve_forever()

    app.run(host='0.0.0.0', port=port, debug=True)