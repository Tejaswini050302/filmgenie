from flask import Flask, request, jsonify
from flask_cors import CORS
from recommender import recommend_by_plot
from mood import detect_mood
from personality import personality_to_query
import random
import os

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "FilmGenie Backend Running"

@app.route("/scene", methods=["POST"])
def scene():
    text = request.json["input"]
    enhanced = text + " movie story"
    return jsonify(recommend_by_plot(enhanced))

@app.route("/mood", methods=["POST"])
def mood():
    text = request.json["text"]
    mood = detect_mood(text)
    return jsonify(recommend_by_plot(mood))

@app.route("/personality", methods=["POST"])
def personality():
    score = request.json["score"]
    query = personality_to_query(score)
    return jsonify(recommend_by_plot(query))

@app.route("/surprise")
def surprise():
    sample_queries = [
        "emotional inspiring story",
        "action adventure",
        "romantic love story",
        "thriller mystery suspense",
        "space sci fi survival"
    ]
    query = random.choice(sample_queries)
    return jsonify(recommend_by_plot(query))

@app.route("/group", methods=["POST"])
def group():
    inputs = request.json["inputs"]
    combined = " ".join(inputs)
    return jsonify(recommend_by_plot(combined))

# IMPORTANT FOR DEPLOYMENT
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
