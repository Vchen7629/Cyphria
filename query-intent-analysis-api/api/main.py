from flask import Flask, request, jsonify
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sbert_ml_model.intent_classifier import classifier

app = Flask("User_Query_intent-api")


@app.route("/", methods=["GET"])
def returnDefault():
    return "You've hit the base route of intent api"

@app.route("/query", methods=["POST"])
def Query():
    if not request.is_json:
        return jsonify({"error": "Request must be Json"}), 400
    
    data = request.json
    category, scores = classifier.classify(data["query"])

    return jsonify({
        "message": "Successfully Sent Query to ml model",
        "predicted_category": category,
    }), 200

if __name__ == "__main__":
    app.run(debug=True)