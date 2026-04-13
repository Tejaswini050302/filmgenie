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

# 🔥 FIX NaN → valid JSON
movies = movies.fillna("")

# Convert to string
movies["overview"] = movies["overview"].astype(str)
movies["genres"] = movies["genres"].astype(str)
movies["keywords"] = movies["keywords"].astype(str)
movies["title"] = movies["title"].astype(str)

# 🔥 COMBINE TEXT (SMART SEARCH)
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
# RECOMMEND (SCENE)
# -------------------------------
@app.route("/recommend")
def recommend():
    query = request.args.get("q", "").lower()

    # 🎲 TRUE RANDOM MODE
    if query == "random":
        return jsonify(movies.sample(12).to_dict(orient="records"))

    results = movies[
        movies["content"].str.lower().str.contains(query, na=False)
    ]

    # fallback if nothing found
    if results.empty:
        return jsonify(movies.sample(12).to_dict(orient="records"))

    return jsonify(results.sample(min(12, len(results))).to_dict(orient="records"))
# -------------------------------
# MOOD
# -------------------------------
@app.route("/mood")
def mood():
    mood = request.args.get("mood", "").lower()

    if mood == "happy":
        query = "comedy"
    elif mood == "sad":
        query = "drama"
    elif mood == "romantic":
        query = "romance"
    else:
        query = "action"

    results = movies[
        movies["content"].str.lower().str.contains(query, na=False)
    ]

    # 🔥 fallback
    if results.empty:
        return jsonify(movies.sample(10).to_dict(orient="records"))

    return jsonify(results.head(10).to_dict(orient="records"))

# -------------------------------
# SURPRISE
# -------------------------------
@app.route("/surprise")
def surprise():
    return jsonify(movies.sample(10).to_dict(orient="records"))

#--------------------------------
# PERSONALITY
#-------------------------------

@app.route("/personality")
def personality():
    score = int(request.args.get("score", 5))

    if score <= 3:
        result = movies[movies["content"].str.contains("romance|drama", case=False, na=False)]
    elif score <= 7:
        result = movies[movies["content"].str.contains("comedy|family", case=False, na=False)]
    else:
        result = movies[movies["content"].str.contains("action|thriller|war", case=False, na=False)]

    return jsonify(result.sample(min(12, len(result))).to_dict(orient="records"))

# -------------------------------
# CHATBOT
# -------------------------------
@app.route("/chat")
def chat():
    msg = request.args.get("msg", "").lower()

    if "sad" in msg:
        reply = "Try watching an emotional drama."
    elif "happy" in msg:
        reply = "Go for a fun comedy!"
    elif "action" in msg:
        reply = "Watch an action thriller!"
    else:
        reply = "Tell me your mood or a scene."

    return jsonify({"reply": reply})

# -------------------------------
# RUN (RENDER)
# -------------------------------
if __name__ == "__main__":
    print("APP STARTED SUCCESSFULLY")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
