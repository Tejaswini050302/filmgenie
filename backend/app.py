from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
import requests

TMDB_API_KEY = "6701680a60181e103f2b432a7e39663c"

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
        result = movies[movies["content"].str.contains("comedy|fun|family", case=False, na=False)]

    elif mood == "sad":
        result = movies[movies["content"].str.contains("drama|emotional|sad", case=False, na=False)]

    elif mood == "romantic":
        result = movies[movies["content"].str.contains("romance|love", case=False, na=False)]

    elif mood == "action":
        result = movies[movies["content"].str.contains("action|war|thriller", case=False, na=False)]

    else:
        result = movies

    # 🎲 RANDOMIZE RESULTS
    return jsonify(result.sample(min(12, len(result))).to_dict(orient="records"))

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
# TRENDING
# -------------------------------

@app.route("/trending")
def trending():
    url = f"https://api.themoviedb.org/3/trending/movie/day?api_key={TMDB_API_KEY}"
    data = requests.get(url).json()
    return jsonify(data.get("results", []))

# -------------------------------
# GENRE
# -------------------------------

@app.route("/genre")
def genre():
    genre_id = request.args.get("id")

    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}"
    data = requests.get(url).json()

    return jsonify(data.get("results", []))

# -------------------------------
# ACTOR
# -------------------------------

@app.route("/actor")
def actor():
    name = request.args.get("name")

    # Step 1: find actor ID
    url1 = f"https://api.themoviedb.org/3/search/person?api_key={TMDB_API_KEY}&query={name}"
    data1 = requests.get(url1).json()

    if not data1.get("results"):
        return jsonify([])

    actor_id = data1["results"][0]["id"]

    # Step 2: get movies
    url2 = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_cast={actor_id}"
    data2 = requests.get(url2).json()

    return jsonify(data2.get("results", []))

# -------------------------------
# SIM
# -------------------------------

@app.route("/similar")
def similar():
    movie = request.args.get("name")

    url1 = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie}"
    data1 = requests.get(url1).json()

    if not data1.get("results"):
        return jsonify([])

    movie_id = data1["results"][0]["id"]

    url2 = f"https://api.themoviedb.org/3/movie/{movie_id}/similar?api_key={TMDB_API_KEY}"
    data2 = requests.get(url2).json()

    return jsonify(data2.get("results", []))

# -------------------------------
# RUN (RENDER)
# -------------------------------
if __name__ == "__main__":
    print("APP STARTED SUCCESSFULLY")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
