



import streamlit as st              
import pandas as pd                 
import yfinance as yf              

# Modules personnalisés
from analys import analyze_sentiment, predict_price
from data import save_to_mysql
# On récupère les accès de manière sécurisée via Streamlit Secrets



# CONFIGURATION DE LA PAGE


st.set_page_config(
    page_title="Projet Finance ",
    layout="wide"
)

# Titre principal
st.title("📈 Projet Finance  Dashboard")



#  SIDEBAR : INPUT UTILISATEUR


ticker = st.sidebar.text_input(
    "Ticker (ex: AAPL, TSLA, MSFT)",
    "AAPL"
).upper()




if st.sidebar.button("Lancer l'Analyse"):

    with st.spinner("Analyse  en cours..."):

       
        #  EXTRACTION DONNÉES
       

        df = yf.download(
            ticker,
            period="6mo",
            interval="1d"
        )

        # Vérification ticker valide
        if df.empty:
            st.error("Ticker invalide")
            st.stop()

        # Correction MultiIndex possible
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df.index.name = "Date"

        

        # Moyenne mobile 20 jours
        df["MA20"] = df["Close"].rolling(20).mean()

        
        #  ANALYSE SENTIMENT 
        

        sentiment, news = analyze_sentiment(ticker)

        
        #  MACHINE LEARNING 
       

        #  version ML renvoie prédiction + score confiance
        prediction, confidence = predict_price(df)

       
        #  PRIX ACTUEL
        

        current_price = float(df["Close"].iloc[-1])

        # Calcul variation %
        variation_pourcent = ((prediction - current_price) / current_price) * 100

        
        #  AFFICHAGE KPI
        

        col1, col2, col3 = st.columns(3)

        # Prix actuel
        col1.metric(
            "Prix Actuel",
            f"{current_price:.2f} $"
        )

        # Sentiment
        col2.metric(
            "Sentiment IA",
            f"{sentiment:.2f}"
        )

        # Prédiction + variation
        col3.metric(
            "Prediction Demain",
            f"{prediction:.2f} $",
            delta=f"{variation_pourcent:.2f} %"
        )

        # Score confiance modèle
        st.caption(f"📊 Score confiance modèle (R²) : {confidence:.2f}")

        
        # VISUALISATION
       

        st.subheader(f"Historique et Tendance : {ticker}")

        # Graphique 
        st.line_chart(
            df[["Close", "MA20"]]
        )

        
        #  SAUVEGARDE MYSQL
       

        save_to_mysql(df, ticker)

        st.success(f"✅ Données sauvegardées dans MySQL pour {ticker}")

        
        #  AFFICHAGE NEWS
       

        st.subheader(f"Dernières actualités marquantes concernant : {ticker}")

        for n in news:
            st.info(n)

        
        # TABLE COMPLETE
        

        with st.expander("Voir les données"):
            st.dataframe(df)