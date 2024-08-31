#N7y

from flask import Flask,redirect,url_for,jsonify, render_template,request,session
import psutil
import time
import hashlib
import json
import datetime
import hashlib
import sqlite3
from os import urandom

app = Flask(__name__)
app.secret_key = hashlib.md5(datetime.now().strftime("%Y%m%d%H%M%S").encode()).hexdigest() + hashlib.md5(urandom(64)).hexdigest()


#product = os.popen("cat /sys/class/dmi/id/product_name").read().strip()
try:
    product = open("/sys/class/dmi/id/product_name","r").read().strip()
except:
    product = "NaN"

class db:
    global c
    global connection
    connection = sqlite3.connect("datab.db",check_same_thread=False)
    c = connection.cursor()

        

    def getpass():
        # safe cursor.execute("SELECT admin FROM users WHERE username = %s'", (username, ));
        try:
            ret = c.execute(f"SELECT passwd FROM uinfo WHERE user='admin';" ) # 
            passwd_blob = ""
            for i in ret:
                passwd_blob += i[0]
            # print(passwd_blob)
            return passwd_blob      
        except:
            return False
    def updatep(np):
        try:
            c.execute(f"UPDATE uinfo set passwd='{np}' WHERE user='admin'") 
            connection.commit()
            return True    
        except:
            return False
    

   

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
    if "loginsession" not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/processes')
def processes():
    if "loginsession" not in session:
        return redirect(url_for('login'))
    return jsonify(prs())

@app.route("/usr")
def u():
    if "loginsession" not in session:
        return redirect(url_for('login'))
    return jsonify(usrs())


@app.route('/conn')
def con():
    if "loginsession" not in session:
        return redirect(url_for('login'))
    return jsonify(conn())

@app.route('/meminfo')
def memi() :
    if "loginsession" not in session:
        return redirect(url_for('login'))
    return jsonify(meminfo())



@app.route('/login', methods=["GET","POST"])
def login():
    error = ""
    
    if request.method == "GET":
        if "loginsession" in session:
            return redirect(url_for('index'))
    

    if request.method == "POST":
        working_passwd = db.getpass()
        try:
            inppasswd = request.form["passwd"]
            md_inppasswd = hashlib.md5(inppasswd.encode()).hexdigest()
            if working_passwd == md_inppasswd:
                # succs
                session['loginsession'] = str(working_passwd + str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")))
                return redirect(url_for('index'))
            else:
                error = "Password Error"
                return render_template('login.html',error=error,product=product)
        except:
            error = "Password Error"
            return render_template('login.html',error=error,product=product)

    return render_template('login.html',error=error,product=product)


@app.route('/chpass', methods=["GET", "POST"])
def chpass():
    if "loginsession" not in session:
        return redirect(url_for('login'))
    if request.method == "POST":
        print("data recved")
        # print(request.form)
        ppasswd = request.form['prvpasswd']
        npasswd = request.form['newpasswd']
        cpasswd = request.form['cpasswd']
        
        ret_pass = db.getpass()

        if npasswd == cpasswd:
            if hashlib.md5(ppasswd.encode()).hexdigest() == ret_pass:
                mdpass = hashlib.md5(npasswd.encode()).hexdigest()
                db.updatep(mdpass)
                print("updated sucess")
                session.pop("loginsession", None)
                return redirect(url_for("login"))
            else:
                print("prev pass not machc real pass")
        else:
            print("pass confirmation failed; ")



    return render_template('chpass.html')



if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=7001,)










