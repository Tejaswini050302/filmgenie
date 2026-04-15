from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
import requests

# 🔥 DATABASE
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# -------------------------------
# CONFIG
# -------------------------------
TMDB_API_KEY = "6701680a60181e103f2b432a7e39663c"

app = Flask(__name__)
CORS(app)

# -------------------------------
# DATABASE
# -------------------------------
engine = create_engine("sqlite:///users.db")
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class UserPref(Base):
    __tablename__ = "preferences"
    id = Column(Integer, primary_key=True)
    type = Column(String)
    value = Column(String)

Base.metadata.create_all(engine)

# -------------------------------
# LOAD DATA
# -------------------------------
movies = pd.read_csv("data/movies.csv")

# 🔥 reduce size (IMPORTANT for Render)
movies = movies.sample(min(2000, len(movies)))

movies = movies.fillna("")
movies["content"] = (
    movies["overview"].astype(str) + " " +
    movies["genres"].astype(str) + " " +
    movies["keywords"].astype(str) + " " +
    movies["title"].astype(str)
)

# -------------------------------
# ML MODEL (LIGHTWEIGHT)
# -------------------------------
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

print("Training lightweight ML model...")

cv = CountVectorizer(max_features=3000, stop_words='english')
vectors = cv.fit_transform(movies["content"])  # ❌ NO toarray()

print("ML ready ✅")

# -------------------------------
# ML RECOMMEND (NO MEMORY CRASH)
# -------------------------------
@app.route("/ml")
def ml_recommend():
    name = request.args.get("name", "").lower()

    idx = movies[movies["title"].str.lower() == name].index
    if len(idx) == 0:
        return jsonify([])

    idx = idx[0]

    # ✅ compute only needed similarity
    sim_scores = cosine_similarity(vectors[idx], vectors).flatten()

    scores = list(enumerate(sim_scores))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:13]

    movie_indices = [i[0] for i in scores]

    return jsonify(movies.iloc[movie_indices].to_dict(orient="records"))

# -------------------------------
# HOME
# -------------------------------
@app.route("/")
def home():
    return "FilmGenie Backend Running!"

# -------------------------------
# TRACK USER
# -------------------------------
@app.route("/track")
def track():
    t = request.args.get("type")
    v = request.args.get("value")

    if t and v:
        session.add(UserPref(type=t, value=v))
        session.commit()

    return jsonify({"status": "saved"})

# -------------------------------
# SMART AI
# -------------------------------
@app.route("/smart")
def smart():
    prefs = session.query(UserPref).all()

    if not prefs:
        return jsonify(movies.sample(12).to_dict(orient="records"))

    keywords = " ".join([p.value for p in prefs])

    result = movies[
        movies["content"].str.contains(keywords, case=False, na=False)
    ]

    if result.empty:
        result = movies

    return jsonify(result.sample(min(12, len(result))).to_dict(orient="records"))

# -------------------------------
# SEARCH
# -------------------------------
@app.route("/recommend")
def recommend():
    query = request.args.get("q", "").lower()

    if query == "random":
        return jsonify(movies.sample(12).to_dict(orient="records"))

    results = movies[
        movies["content"].str.lower().str.contains(query, na=False)
    ]

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
        result = movies[movies["content"].str.contains("comedy|fun|family", case=False)]
    elif mood == "sad":
        result = movies[movies["content"].str.contains("drama|sad", case=False)]
    elif mood == "romantic":
        result = movies[movies["content"].str.contains("romance|love", case=False)]
    elif mood == "action":
        result = movies[movies["content"].str.contains("action|war|thriller", case=False)]
    else:
        result = movies

    return jsonify(result.sample(min(12, len(result))).to_dict(orient="records"))

# -------------------------------
# SURPRISE
# -------------------------------
@app.route("/surprise")
def surprise():
    return jsonify(movies.sample(10).to_dict(orient="records"))

# -------------------------------
# PERSONALITY
# -------------------------------
@app.route("/personality")
def personality():
    score = int(request.args.get("score", 5))

    if score <= 15:
        result = movies[movies["content"].str.contains("romance|drama", case=False)]
    elif score <= 25:
        result = movies[movies["content"].str.contains("comedy|family", case=False)]
    else:
        result = movies[movies["content"].str.contains("action|thriller", case=False)]

    return jsonify(result.sample(min(12, len(result))).to_dict(orient="records"))

# -------------------------------
# CHAT
# -------------------------------
@app.route("/chat")
def chat():
    msg = request.args.get("msg", "").lower()

    if "sad" in msg:
        reply = "Try emotional drama."
    elif "happy" in msg:
        reply = "Watch comedy!"
    elif "action" in msg:
        reply = "Go for action thriller!"
    else:
        reply = "Tell me mood or scene."

    return jsonify({"reply": reply})

# -------------------------------
# TMDB APIs
# -------------------------------
@app.route("/trending")
def trending():
    data = requests.get(f"https://api.themoviedb.org/3/trending/movie/day?api_key={TMDB_API_KEY}").json()
    return jsonify(data.get("results", []))

@app.route("/genre")
def genre():
    gid = request.args.get("id")
    data = requests.get(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={gid}").json()
    return jsonify(data.get("results", []))

@app.route("/actor")
def actor():
    name = request.args.get("name")
    d1 = requests.get(f"https://api.themoviedb.org/3/search/person?api_key={TMDB_API_KEY}&query={name}").json()

    if not d1.get("results"):
        return jsonify([])

    actor_id = d1["results"][0]["id"]

    d2 = requests.get(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_cast={actor_id}").json()
    return jsonify(d2.get("results", []))

@app.route("/similar")
def similar():
    name = request.args.get("name")

    d1 = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={name}").json()
    if not d1.get("results"):
        return jsonify([])

    mid = d1["results"][0]["id"]

    d2 = requests.get(f"https://api.themoviedb.org/3/movie/{mid}/similar?api_key={TMDB_API_KEY}").json()
    return jsonify(d2.get("results", []))

# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    print("APP STARTED SUCCESSFULLY")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
