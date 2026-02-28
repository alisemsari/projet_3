

import pandas as pd
import numpy as np
import yfinance as yf
from textblob import TextBlob
from GoogleNews import GoogleNews

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score




def analyze_sentiment(ticker_symbol):
    """
    Analyse le sentiment global des news liées au ticker.
    Retourne :
    - Score moyen de sentiment (-1 à +1)
    - 2 titres récents pour affichage
    """

    news_titles = []

    
    try:
        stock = yf.Ticker(ticker_symbol)
        if stock.news:
            for item in stock.news:
                title = item.get('title')
                if title:
                    news_titles.append(title)
    except:
        pass

    
    if not news_titles:
        try:
            googlenews = GoogleNews(lang='en', region='US', period='7d')
            googlenews.search(f"{ticker_symbol} stock market")
            results = googlenews.result()

            for res in results:
                t = res.get('title')
                if t:
                    news_titles.append(t)
        except:
            return 0.0, ["Erreur de connexion aux sources"]

    
    sentiments = []

    for title in news_titles:
        blob = TextBlob(title)
        sentiments.append(blob.sentiment.polarity)

    if sentiments:
        avg_sentiment = sum(sentiments) / len(sentiments)
        return avg_sentiment, news_titles[:2]

    return 0.0, ["Aucune actualité trouvée"]




def predict_price(df, window=60):
    """
    Prédiction avancée du prix du lendemain
    en utilisant plusieurs indicateurs financiers.

    Paramètre :
    window = nombre de jours récents utilisés
    window=60 = on utilise uniquement les 60 derniers jours
    """

    
    df_ml = df.copy().tail(window)

    

    # Rendement journalier (% variation) 100 → 110 = +10% profil dans la journé
    df_ml["Return"] = df_ml["Close"].pct_change()

    # Volatilité (écart-type des rendements sur 10 jours)
    df_ml["Volatility"] = df_ml["Return"].rolling(10).std()

    # Lag1 = prix de la veille
    df_ml["Lag1"] = df_ml["Close"].shift(1)

    # Moyenne mobile 20 jours 
    df_ml["MA20"] = df_ml["Close"].rolling(20).mean()

    # Moyenne mobile 50 jours
    df_ml["MA50"] = df_ml["Close"].rolling(50).mean()

    # Suppression des lignes NaN générées
    df_ml = df_ml.dropna()

   
    # Définition X (features) et y (target)
    

    X = df_ml[["Lag1", "MA20", "MA50", "Volatility"]]
    y = df_ml["Close"]

    
    #  Normalisation des données
    # important car features différentes échelles)
   

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    
    #  Entraînement du modèle
   

    model = LinearRegression()
    model.fit(X_scaled, y)

    
    # Évaluation du modèle (score confiance)
    

    y_pred_train = model.predict(X_scaled)
    confidence = r2_score(y, y_pred_train)

    
    #  Prédiction pour le jour suivant
    

    # On récupère la dernière ligne
    last_row = df_ml.iloc[-1]

    # On construit les features pour demain
    next_features = pd.DataFrame([[
        last_row["Close"],      # Lag1 = prix actuel
        last_row["MA20"],
        last_row["MA50"],
        last_row["Volatility"]
    ]], columns=["Lag1", "MA20", "MA50", "Volatility"])

    # Normalisation
    next_scaled = scaler.transform(next_features)

    # Prédiction
    prediction = model.predict(next_scaled)

    return float(prediction[0]), float(confidence)