from flask import Flask, request, jsonify
from flask_cors import CORS
from recommender import recommend_by_plot
from mood import detect_mood
from personality import personality_to_query
import random
import os

print("APP STARTED SUCCESSFULLY")

from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "FilmGenie Backend Running!"

if __name__ == "__main__":
    print("APP STARTED SUCCESSFULLY")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
