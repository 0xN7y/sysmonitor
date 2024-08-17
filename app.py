#N7y

from flask import Flask, jsonify, render_template
import psutil
import time
import hashlib
import json
import datetime

app = Flask(__name__)



def usrs():

    ret = []
    usr = psutil.users()
    for i in usr:
        ret.append(str("[Name] : "+i.name+", [PID] : "+str(i.pid)+", [Host] : "+i.host+", [Terminal] : "+i.terminal+", [Started] : "+str(datetime.datetime.fromtimestamp(i.started).strftime("%A, %B %d, %Y %I:%M:%S"))))
    return ret    



def conn():  
    ret = []
    for i in psutil.net_connections():
        if i.raddr:
            ret.append(i.raddr.ip+":"+str(i.raddr.port)+" status : "+i.status)                   
    return ret

def prs():
    processes = []

    for pr in psutil.process_iter(['pid', 'name', 'username','status']):
        # print(pr.info)
        try:
            f = open("/proc/"+str(pr.info['pid'])+"/exe", "rb").read()    
            fh = hashlib.md5(f).hexdigest()
        except:
            fh = "coudnt hash"
        a = pr.info
        a["hash"] = fh
        processes.append(a)
    return processes[::-1]

def meminfo():
    cpu = psutil.cpu_percent(interval=1)

    mem = psutil.virtual_memory()
    memory_usage = mem.percent
    

    storage = psutil.disk_usage('/')
    storage_ = storage.percent

    return {
        'cpu_usage': cpu,
        'memory_usage': memory_usage,
        'disk_usage': storage_,
    }


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processes')
def processes():
    return jsonify(prs())

@app.route("/usr")
def u():
    return jsonify(usrs())


@app.route('/conn')
def con():
    return jsonify(conn())

@app.route('/meminfo')
def memi() :
    return jsonify(meminfo())

if __name__ == '__main__':
    app.run(debug=True)










