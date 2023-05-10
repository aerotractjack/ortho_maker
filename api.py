from flask import Flask, request, jsonify, render_template
from orthoq import OrthoQ

app = Flask(__name__, template_folder="templates")
q = OrthoQ("~/ORTHO_Q")

@app.route("/status")
def status():
    ''' determine if machine is currently running export and 
    how many are in the queue '''
    contents = q.contents
    queue_len = len(contents)
    busy = queue_len > 0
    resp_body = {
        "busy": busy, "queue_len": queue_len,
        "contents": q.contents
    }
    return jsonify(resp_body)

@app.route("/q/submit/server", methods=["POST"])
def q_submit_server():
    ''' show a message saying the ortho was successfully submitted q'''
    name = request.form["expName"]
    paths = request.form['expPaths']
    dest = request.form['expDest']
    qpath = q.push(name, paths, dest)
    return jsonify({"status": submitted})
    # return render_template("submitted.html", submission_name=name, 
    #                        submission_paths=paths, submission_dest=dest,
    #                        qloc=qpath)