import pandas as pd
import numpy as np
import yfinance as yf
from textblob import TextBlob
import feedparser

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score


# =========================================
# SENTIMENT ANALYSIS (VERSION FIX RSS)
# =========================================

def analyze_sentiment(ticker_symbol):

    news_titles = []

    # ===============================
    # 1. RSS GOOGLE NEWS (FIABLE)
    # ===============================
    try:
        url = f"https://news.google.com/rss/search?q={ticker_symbol}+stock&hl=en-US&gl=US&ceid=US:en"

        feed = feedparser.parse(url)

        for entry in feed.entries[:10]:
            news_titles.append(entry.title)

        print("RSS news:", news_titles)

    except Exception as e:
        print("Erreur RSS:", e)
        return 0.0, ["Erreur récupération news"]

    # ===============================
    # 2. SI VIDE
    # ===============================
    if len(news_titles) == 0:
        return 0.0, [f"Aucune news trouvée pour {ticker_symbol}"]

    # ===============================
    # 3. SENTIMENT
    # ===============================
    sentiments = []

    for title in news_titles:
        try:
            blob = TextBlob(title)
            sentiments.append(blob.sentiment.polarity)
        except Exception as e:
            print("Erreur TextBlob:", e)

    # ===============================
    # 4. SCORE FINAL
    # ===============================
    if len(sentiments) > 0:
        avg_sentiment = sum(sentiments) / len(sentiments)
        return avg_sentiment, news_titles[:5]

    return 0.0, ["Erreur analyse sentiment"]


# =========================================
# MACHINE LEARNING
# =========================================

def predict_price(df, window=60):

    df_ml = df.copy().tail(window)

    df_ml["Return"] = df_ml["Close"].pct_change()
    df_ml["Volatility"] = df_ml["Return"].rolling(10).std()
    df_ml["Lag1"] = df_ml["Close"].shift(1)
    df_ml["MA20"] = df_ml["Close"].rolling(20).mean()
    df_ml["MA50"] = df_ml["Close"].rolling(50).mean()

    df_ml = df_ml.dropna()

    X = df_ml[["Lag1", "MA20", "MA50", "Volatility"]]
    y = df_ml["Close"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = LinearRegression()
    model.fit(X_scaled, y)

    y_pred_train = model.predict(X_scaled)
    confidence = r2_score(y, y_pred_train)

    last_row = df_ml.iloc[-1]

    next_features = pd.DataFrame([[
        last_row["Close"],
        last_row["MA20"],
        last_row["MA50"],
        last_row["Volatility"]
    ]], columns=["Lag1", "MA20", "MA50", "Volatility"])

    next_scaled = scaler.transform(next_features)

    prediction = model.predict(next_scaled)

    return float(prediction[0]), float(confidence)