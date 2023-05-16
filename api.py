from flask import Flask, request, jsonify
from orthoq import OrthoQ

app = Flask(__name__, template_folder="templates")
q = OrthoQ("~/ORTHO_Q")

@app.route("/status")
def status():
    ''' determine if machine is currently running export and 
    how many are in the queue '''
    contents, bodies = q.contents
    queue_len = len(contents)
    busy = queue_len > 0
    resp_body = {
        "busy": busy, "queue_len": queue_len,
        "contents": contents,
        "bodies": bodies
    }
    return jsonify(resp_body)

@app.route("/q/submit/server", methods=["POST"])
def q_submit_server():
    ''' show a message saying the ortho was successfully submitted q'''
    submission = request.get_json()
    qpath = q.push(submission)
    return jsonify(request.get_json())