from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# -------------------------------
# LOAD DATA
# -------------------------------
movies = pd.read_csv("data/movies.csv")

# Convert columns to string
movies["overview"] = movies["overview"].astype(str)
movies["genres"] = movies["genres"].astype(str)
movies["keywords"] = movies["keywords"].astype(str)
movies["title"] = movies["title"].astype(str)

# 🔥 CREATE ONE SEARCH FIELD (IMPORTANT)
movies["content"] = (
    movies["overview"] + " " +
    movies["genres"] + " " +
    movies["keywords"] + " " +
    movies["title"]
)

# -------------------------------
# HOME
# -------------------------------
@app.route("/")
def home():
    return "FilmGenie Backend Running!"

# -------------------------------
# SCENE / SEARCH
# -------------------------------
@app.route("/recommend")
def recommend():
    query = request.args.get("q", "").lower()

    if not query:
        return jsonify([])

    results = movies[
        movies["content"].str.lower().str.contains(query, na=False)
    ]

    return jsonify(results.head(10).to_dict(orient="records"))

# -------------------------------
# MOOD
# -------------------------------
@app.route("/mood")
def mood():
    mood = request.args.get("mood", "").lower()

    if mood == "happy":
        query = "comedy fun family"
    elif mood == "sad":
        query = "drama emotional"
    elif mood == "romantic":
        query = "romance love"
    else:
        query = "action thriller"

    results = movies[
        movies["content"].str.lower().str.contains(query, na=False)
    ]

    return jsonify(results.head(10).to_dict(orient="records"))

# -------------------------------
# SURPRISE
# -------------------------------
@app.route("/surprise")
def surprise():
    return jsonify(movies.sample(10).to_dict(orient="records"))

# -------------------------------
# CHATBOT
# -------------------------------
@app.route("/chat")
def chat():
    msg = request.args.get("msg", "").lower()

    if "sad" in msg:
        reply = "Watch a drama like Titanic."
    elif "happy" in msg:
        reply = "Try a comedy movie!"
    elif "action" in msg:
        reply = "Go for an action thriller!"
    else:
        reply = "Tell me your mood or a scene you like."

    return jsonify({"reply": reply})

# -------------------------------
# RUN (RENDER FIX)
# -------------------------------
if __name__ == "__main__":
    print("APP STARTED SUCCESSFULLY")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
