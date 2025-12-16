from flask import Flask, request, jsonify
import os
import time
import threading

app = Flask(__name__)

CONSISTENCY_MODE = os.getenv("CONSISTENCY_MODE", "strong")

nodes = {
    "node1": {"value": 0},
    "node2": {"value": 0},
    "node3": {"value": 0}
}

def strong_write(value):
    for n in nodes:
        nodes[n]["value"] = value

def weak_write(value):
    nodes["node1"]["value"] = value

def eventual_write(value):
    nodes["node1"]["value"] = value

    def replicate():
        time.sleep(3)
        for n in nodes:
            nodes[n]["value"] = value

    threading.Thread(target=replicate).start()

@app.route("/write", methods=["POST"])
def write():
    data = request.json
    value = data.get("value")

    if CONSISTENCY_MODE == "strong":
        strong_write(value)
        mode = "STRONG CONSISTENCY"
    elif CONSISTENCY_MODE == "weak":
        weak_write(value)
        mode = "WEAK CONSISTENCY"
    else:
        eventual_write(value)
        mode = "EVENTUAL CONSISTENCY"

    return jsonify({
        "mode": mode,
        "written_value": value,
        "nodes": nodes
    })

@app.route("/read/<node>", methods=["GET"])
def read(node):
    return jsonify({
        "node": node,
        "value": nodes[node]["value"]
    })

@app.route("/")
def index():
    return jsonify({
        "app": "Distributed Flask App",
        "consistency_mode": CONSISTENCY_MODE
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
