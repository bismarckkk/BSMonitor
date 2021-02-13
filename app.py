from flask import Flask, render_template, request, abort, redirect, url_for
import socket
import webbrowser
import qrcode
import packages
import traceback
import copy

try:
    import ujson as json
except:
    import json
from flask_socketio import SocketIO
import os

cname = socket.getfqdn(socket.gethostname())
ip = socket.gethostbyname(cname)

path = os.path.realpath(__file__)
path = os.path.dirname(path)
template_folder = os.path.join(path, 'templates')
static_folder = os.path.join(path, 'static')
app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
app.config['SECRET_KEY'] = 'eagwbilgbewi'
socketio = SocketIO(app, async_mode='gevent', logger=True, engineio_logger=True)
packs = packages.Packs(socketio)
config = packages.Config()
lastConnect = []


@socketio.on('connect', namespace='/ws')
def test_connect():
    print('Client connected')


@socketio.on('disconnect', namespace='/ws')
def test_disconnect():
    print('Client disconnected')


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/chart')
def chart():
    return render_template('chart.html')


@app.route('/list')
def rlist():
    return render_template('list.html')


@app.route('/pList')
def pList():
    names = config.readFilesName()
    re = []
    for it in names:
        status = 0
        if it in packs.packs.keys():
            status = 1
            if it in packs.error.keys():
                status = 2
        re.append({'name': it, 'status': status})
    return json.dumps(re)


@app.route('/start')
def startThread():
    name = request.args.get('p')
    if name is None:
        abort(400)
    info = config.readConfig(name)
    if packs.startThread(name, info['type'], info['config']):
        return '连接成功'
    else:
        return '出现异常错误'


@app.route('/startLast')
def startLast():
    if lastConnect is not None:
        ok = True
        for name in lastConnect:
            info = config.readConfig(name)
            if not packs.startThread(name, info['type'], info['config']):
                ok = False
        if ok:
            return '连接成功'
        else:
            return '出现异常错误'
    else:
        return '还没有连接过设备'


@app.route('/stop')
def stopThread():
    name = request.args.get('p')
    if name is None:
        abort(400)
    try:
        packs.stopThread(name)
    except:
        return '出现异常错误'
    return '断开连接成功'


@app.route('/stopAll')
def stopAll():
    global lastConnect
    try:
        lastConnect = copy.deepcopy(list(packs.packs.keys()))
        for name in lastConnect:
            packs.stopThread(name)
    except:
        print(traceback.format_exc())
        return '出现异常错误'
    return '断开连接成功'


@app.route('/errorInfo')
def errorInfo():
    p = request.args.get('p')
    if p in packs.error.keys():
        return packs.error[p]
    abort(404)


@app.route('/edit')
def edit():
    method = request.args.get('t')
    name = request.args.get('p')
    cfg = {}
    if name is not None:
        info = config.readConfig(name)
        method = info['type']
        cfg = info['config']
    methods = packs.names
    if method is None:
        return render_template('edit.html', methods=methods)
    else:
        if os.path.exists(os.path.join(template_folder, 'methods/%s.html' % method)):
            if name is None:
                name = request.args.get('n')
            return render_template('methods/%s.html' % method, cfg=cfg, showMore=True, methods=methods, selected=method,
                                   name=name)
        else:
            abort(404)


@app.route('/editSubmit', methods=['POST'])
def editSubmit():
    form = request.form.to_dict()
    print(form)
    name = form['name']
    type = form['method']
    del form['name']
    del form['method']
    config.setConfig(name, type, form)
    return redirect(url_for('rlist'))


@app.errorhandler(404)
def error404(_):
    return render_template('404.html'), 404


@app.errorhandler(500)
def error500(_):
    return render_template('500.html'), 500


if __name__ == '__main__':
    port = 8880
    url = 'http://%s:%i' % (ip, port)
    webbrowser.open(url)
    packs.start()

    # server = WSGIServer(('127.0.0.1', 8880), app)
    # webbrowser.open(url)
    # server.serve_forever()

    socketio.run(app, host='0.0.0.0', port=port)
