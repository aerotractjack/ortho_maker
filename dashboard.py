from flask import Flask, render_template, request, jsonify
import requests
from orthoq import OrthoQ
from orthoq_load_balancer import OrthoQLoadBalancer

'''
Simple Flask app to intake orthomosaic processing requests
'''

app = Flask(__name__, template_folder="templates")
q = OrthoQ("~/ORTHO_Q")
lb = OrthoQLoadBalancer()

@app.route("/index")
def index():
    ''' index method '''
    return render_template("index.html")

@app.route("/health")
def health():
    ''' health check '''
    return render_template("health.html")

@app.route("/q/contents")
def q_contents():
    ''' view contents of the queue '''
    return render_template("contents.html", contents=q.contents)

@app.route("/q/submit", methods=["POST", "GET"])
def q_submit():
    ''' render submission form '''
    return render_template("submit.html")

@app.route("/q/submit/server", methods=["POST"])
def q_submit_server():
    ''' show a message saying the ortho was successfully submitted q'''
    name = request.form["expName"]
    paths = request.form['expPaths'].strip("\r\n").split("\r\n")
    paths = [p for p in paths if p != '']
    dest = request.form['expDest']
    clean_request = {"name": name, "paths": paths, "dest": dest}
    lb_check = lb.check_statuses()
    lb_url = "http://192.168.1.41:5005" + "/q/submit/server"
    res = requests.post(lb_url, json=clean_request)
    resp = {
        "load_balancer_response": lb_check,
        "submission_response": res.json()
    }
    # qpath = q.push(name, paths, dest)
    return jsonify(resp)
    # return render_template("submitted.html", submission_name=name, 
    #                        submission_paths=paths, submission_dest=dest,
    #                        qloc=qpath)

