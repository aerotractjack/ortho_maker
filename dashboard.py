from flask import Flask, render_template, request, jsonify
import requests
from orthoq_load_balancer import OrthoQLoadBalancer
from orthoq import OrthoQ
'''
Simple Flask app to intake orthomosaic processing requests
'''

app = Flask(__name__, template_folder="templates")
lb = OrthoQLoadBalancer()
complete_Q = OrthoQ("/home/aerotract/NAS/main/OrthoQ_finished")

data = {
    "Company1": {
        "C1P1xxxxx": ["C1P1S1", "C1P1S2"],
        "C1P2": ["C1P2S1", "C1P2S2"],
    },
    "Company2": {
        "C2P1": ["C2P1S1", "C2P1S2"],
        "C2P2": ["C2P2S1", "C2P2S2"],
    }
}

@app.after_request
def add_header(response):
    ''' make sure we are not caching responses '''
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route("/index")
def index():
    ''' index method '''
    return render_template("index.html")

@app.route("/complete")
def complete():
    ''' display completed runs '''
    contents, bodies = complete_Q.contents
    N = len(contents)
    return render_template("complete.html", contents=contents, names=bodies, N=N)

@app.route("/statuses")
def statuses():
    ''' check the statuses of each worker '''
    stats = lb.show_all_statuses()
    return render_template("statuses.html", statuses=stats, submission_content=None)

@app.route("/health")
def health():
    ''' health check '''
    return render_template("health.html")

@app.route("/q/submit", methods=["POST", "GET"])
def q_submit():
    ''' render submission form '''
    comps = list(data.keys())
    return render_template("submit.html", companies=comps)

@app.route("/q/submit/server", methods=["POST"])
def q_submit_server():
    ''' show a message saying where the ortho was submitted '''
    name = request.form["expName"]
    paths = request.form['expPaths'].strip("\r\n").split("\r\n")
    paths = [p for p in paths if p != '']
    dest = request.form['expDest']
    clean_request = {
        "name": name, "paths": paths, "dest": dest,
        "company": request.form["company"],
        "project": request.form["project"],
        "site": request.form["site"]
    }
    lb_check = lb.check_statuses()
    lb_url = lb_check["url"] + "/q/submit/server"
    res = requests.post(lb_url, json=clean_request)
    response = {
        "load_balancer_response": lb_check,
        "submission_response": res.json()
    }
    stats = lb.show_all_statuses()
    return render_template("statuses.html", statuses=stats, submission_content=response)

@app.route("/q/remove", methods=["POST"])
def q_remove():
    data = request.get_json()
    try:
        complete_Q.remove(data["filename"])
    except FileNotFoundError as fnfe:
        print(fnfe)
    return jsonify({"success": True, "data": data})

@app.route("/options/<company>")
def options_company(company):
    sel = data[company]
    resp = []
    for (k,v) in sel.items():
        r = {"value": k, "label": k}
        resp.append(r)
    return jsonify(resp)

@app.route("/options/<company>/<site>")
def options_company_site(company, site):
    sel = data[company][site]
    resp = []
    for s in sel:
        r = {"value": s, "label": s}
        resp.append(r)
    return jsonify(resp)