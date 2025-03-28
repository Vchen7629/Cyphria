from flask import Flask, request, jsonify
import sys
import os
import json
import threading

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from apachespark import main

app = Flask("Apache-Spark-Pipeline")


@app.route("/", methods=["GET"])
def returnDefault():
    return "You've hit the base route of intent api"

@app.route("/query", methods=["POST"])
def PostData():
    if not request.is_json:
        return jsonify({"error": "Request must be Json"}), 400
    
    data = request.json
    main.Spark.inputData(data)

    return jsonify({
        "message": "Successfully Sent Query to ml model",
    }), 200

@app.route("/batch", methods=["POST"])
def Process_Batch():
    batchCount = main.Spark.Process_Batch()
    return jsonify({
        "message": "Successfully Generated Vector Embeddings for batch",
        "Batch Count": batchCount,
    }), 200
    
if __name__ == "__main__":
    app.run(debug=True, threaded=True)