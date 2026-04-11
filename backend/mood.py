from textblob import TextBlob

def detect_mood(text):
    polarity = TextBlob(text).sentiment.polarity

    if polarity > 0.5:
        return "happy inspiring feel good movie"
    elif polarity < -0.5:
        return "sad emotional deep story"
    else:
        return "light entertaining movie"