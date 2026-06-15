from textblob import TextBlob

def detect_emotion(text):

    polarity = TextBlob(text).sentiment.polarity

    if polarity > 0.3:
        return "Happy 😊"

    elif polarity < -0.3:
        return "Sad 😔"

    else:
        return "Neutral 😐"