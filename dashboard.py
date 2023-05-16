from flask import Flask, render_template, request, jsonify
import requests
from orthoq_load_balancer import OrthoQLoadBalancer
import sys
'''
Simple Flask app to intake orthomosaic processing requests
'''

app = Flask(__name__, template_folder="templates")
lb = OrthoQLoadBalancer()

@app.route("/index")
def index():
    ''' index method '''
    return render_template("index.html")

@app.route("/statuses")
def statuses():
    ''' check the statuses of each worker '''
    stats = lb.show_all_statuses()
    return render_template("statuses.html", statuses=stats)

@app.route("/health")
def health():
    ''' health check '''
    return render_template("health.html")

@app.route("/q/submit", methods=["POST", "GET"])
def q_submit():
    ''' render submission form '''
    return render_template("submit.html")

@app.route("/q/submit/server", methods=["POST"])
def q_submit_server():
    ''' show a message saying where the ortho was submitted '''
    name = request.form["expName"]
    paths = request.form['expPaths'].strip("\r\n").split("\r\n")
    paths = [p for p in paths if p != '']
    dest = request.form['expDest']
    clean_request = {"name": name, "paths": paths, "dest": dest}
    lb_check = lb.check_statuses()
    lb_url = lb_check["url"] + "/q/submit/server"
    res = requests.post(lb_url, json=clean_request)
    print(lb_url)
    sys.stdout.flush()
    print(res)
    sys.stdout.flush()
    response = {
        "load_balancer_response": lb_check,
        "submission_response": res.json()
    }
    return render_template("submitted.html", content=response)

