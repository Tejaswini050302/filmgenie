def personality_to_query(score):
    if score > 7:
        return "complex intelligent emotional story"
    elif score > 4:
        return "balanced drama and entertainment"
    else:
        return "fun comedy action movie"