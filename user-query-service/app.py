from flask import Flask, request, jsonify

from api_routes import topictrends, categorytrends, comparisontrends, subreddittrends

app = Flask("User_Query_intent-api")


@app.route("/", methods=["GET"])
def returnDefault():
    return "You've hit the base route of intent api"
    
@app.route("/trends/topic", methods=["POST"])
def topic():
    if not request.is_json:
        return jsonify({"error": "Request must be Json"}), 400
    
    data = request.json
    response = topictrends.topic.retrieve_relevant_posts(data["query"])
    
    return jsonify({
        "message": "Successfully Sent Query to ml model",
        "response": response,
    }), 200

    
@app.route("/trends/category", methods=["POST"])
def category():
    if not request.is_json:
        return jsonify({"error": "Request must be Json"}), 400
    
    data = request.json
    response = categorytrends.category.retrieve_relevant_posts(data["query"])
    
    return jsonify({
        "message": "Successfully Sent Query to ml model",
        "response": response,
    }), 200

@app.route("/trends/subreddit", methods=["POST"])
def subreddit():
    if not request.is_json:
        return jsonify({"error": "Request must be Json"}), 400
    
    data = request.json
    

@app.route("/trends/comparison", methods=["POST"])
def comparison():
    if not request.is_json:
        return jsonify({"error": "Request must be Json"}), 400
    data = request.json
    
    response = comparisontrends.comparison.retrieve_relevant_posts(data["query"])
    
    return jsonify({
        "message": "Successfully Sent Query to ml model",
        "response": response,
    }), 200


if __name__ == "__main__":
    app.run(debug=True)