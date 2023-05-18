from flask import Flask, render_template, request, jsonify
import requests
import os 
from orthoq_load_balancer import OrthoQLoadBalancer
from orthoq import OrthoQ
'''
Simple Flask app to intake orthomosaic processing requests
'''

app = Flask(__name__, template_folder="templates")
app.debug = True
lb = OrthoQLoadBalancer()
complete_Q = OrthoQ("/home/aerotract/NAS/main/OrthoQ_finished")
NASclients = "/home/aerotract/NAS/main/Clients"

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
    comps = os.listdir(NASclients)
    return render_template("submit.html", companies=comps)

@app.route("/q/submit/server", methods=["POST"])
def q_submit_server():
    ''' show a message saying where the ortho was submitted '''
    # name = request.form["expName"]
    # paths = request.form['expPaths'].strip("\r\n").split("\r\n")
    # paths = [p for p in paths if p != '']
    sel_paths = request.form.getlist('source_image_option')
    dest_dir = request.form['expDest']
    if len(dest_dir.strip(" ")) == 0:
        dest_dir = "ortho"
    comp = request.form["company"]
    proj = request.form["project"]
    site = request.form["site"]
    name = f"{comp}-{proj}-{site}"
    abs_paths = []
    dest = os.path.join(NASclients, comp, proj, site, "Data", dest_dir)
    for sp in sel_paths:
        ap = os.path.join(NASclients, comp, proj, site, "Data", "src_imgs", sp)
        abs_paths.append(ap)
    clean_request = {
        "name": name, "paths": abs_paths, "dest": dest,
        "company": comp, "project": proj, "site": site
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
    sel = os.listdir(os.path.join(NASclients, company))
    resp = []
    for s in sel:
        r = {"value": s, "label": s}
        resp.append(r)
    return jsonify({"dropdown": resp})

@app.route("/options/<company>/<project>")
def options_company_project(company, project):
    sel = os.listdir(os.path.join(NASclients, company, project))
    dropdown = []
    for s in sel:
        r = {"value": s, "label": s}
        dropdown.append(r)
    return jsonify({"dropdown": dropdown})

@app.route("/options/<company>/<project>/<site>")
def options_company_project_site(company, project, site):
    sel = os.listdir(os.path.join(NASclients, company, project, site, "Data", "src_imgs"))
    checkpointMenu = []
    for s in sel:
        r = {"value": s, "label": s}
        checkpointMenu.append(r)
    return jsonify({"checkpointMenu": checkpointMenu})

if __name__ == '__main__':
    app.run(port=5001)