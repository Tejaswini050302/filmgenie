from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# Load dataset
movies = pd.read_csv("data/movies.csv")

movies["genres"] = movies["genres"].astype(str)
movies["keywords"] = movies["keywords"].astype(str)
movies["overview"] = movies["overview"].astype(str)

# -------------------------------
# HOME ROUTE (TEST)
# -------------------------------
@app.route("/")
def home():
    return "FilmGenie Backend Running!"

# -------------------------------
# SCENE / TEXT BASED RECOMMENDATION
# -------------------------------

@app.route("/recommend")
def recommend():
    query = request.args.get("q", "").lower()

    if not query:
        return jsonify([])

    results = movies[
        (movies["overview"].str.lower().str.contains(query, na=False)) |
        (movies["genres"].str.lower().str.contains(query, na=False)) |
        (movies["keywords"].str.lower().str.contains(query, na=False))
    ]

    return jsonify(results.head(10).to_dict(orient="records"))

# -------------------------------
# MOOD BASED RECOMMENDATION
# -------------------------------
@app.route("/mood")
def mood():
    mood = request.args.get("mood", "").lower()

    if mood == "happy":
        keywords = ["comedy", "fun", "family"]
    elif mood == "sad":
        keywords = ["drama", "emotional"]
    elif mood == "romantic":
        keywords = ["romance", "love"]
    else:
        keywords = ["action", "thriller"]

    results = movies[
        movies["genres"].str.lower().apply(
            lambda x: any(word in x for word in keywords)
        )
    ]

    return jsonify(results.head(10).to_dict(orient="records"))

# -------------------------------
# SURPRISE FEATURE
# -------------------------------
@app.route("/surprise")
def surprise():
    results = movies.sample(10)
    return jsonify(results.to_dict(orient="records"))

# -------------------------------
# CHATBOT (SIMPLE)
# -------------------------------
@app.route("/chat")
def chat():
    msg = request.args.get("msg", "").lower()

    if "sad" in msg:
        return jsonify({"reply": "Try watching an emotional drama like Titanic."})
    elif "happy" in msg:
        return jsonify({"reply": "Go for a fun movie like The Mask!"})
    elif "action" in msg:
        return jsonify({"reply": "You might enjoy The Dark Knight!"})
    else:
        return jsonify({"reply": "Tell me your mood or a scene you like!"})

# -------------------------------
# RUN APP (IMPORTANT FOR RENDER)
# -------------------------------
if __name__ == "__main__":
    print("APP STARTED SUCCESSFULLY")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
