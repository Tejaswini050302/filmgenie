import pandas as pd
import ast
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_csv("data/movies.csv")

def convert(obj):
    try:
        return [i['name'] for i in ast.literal_eval(obj)]
    except:
        return []

if 'genres' in df.columns:
    df['genres'] = df['genres'].apply(convert)
else:
    df['genres'] = [[] for _ in range(len(df))]

if 'keywords' in df.columns:
    df['keywords'] = df['keywords'].apply(convert)
else:
    df['keywords'] = [[] for _ in range(len(df))]

df['tags'] = (
    df['overview'].fillna('') + " " +
    df['genres'].apply(lambda x: " ".join(x)) + " " +
    df['keywords'].apply(lambda x: " ".join(x))
)

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z ]', '', text)
    return text

df['tags'] = df['tags'].apply(clean_text)

model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(df['tags'].tolist())

def recommend_by_plot(text):
    text = clean_text(text)
    user_emb = model.encode([text])
    scores = cosine_similarity(user_emb, embeddings)[0]

    top_indices = scores.argsort()[::-1]

    results = []
    for i in top_indices:
        if scores[i] > 0.3:
            results.append({
                "title": df.iloc[i]['title'],
                "score": float(scores[i]),
                "reason": "Similar story/theme"
            })
        if len(results) == 5:
            break

    return results