import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st

# CONFIGURATION BASE DE DONNEES
db_config = st.secrets["mysql"]

USER = db_config["user"]
PASSWORD = db_config["password"]
HOST = db_config["host"]
PORT = db_config["port"]
DB_NAME = db_config["database"]

# Création de l'URL de connexion SQLAlchemy
connection_url = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

# Création du moteur SQLAlchemy
engine = create_engine(
    connection_url, 
    echo=False, 
    # Correction SSL pour Aiven : "check_hostname": False est plus robuste que "fake_config"
    connect_args={"ssl": {"check_hostname": False}} 
)

# FONCTION : SAUVEGARDE DATAFRAME
def save_to_mysql(df, table_name):
    try:
        # Nettoyage du nom de table
        target_table = table_name.lower().strip()

        # Nom de la colonne index important pour garder la date
        df.index.name = "Date"

        # Sauvegarde du DataFrame en SQL
        # if_exists="replace" s'occupe tout seul de supprimer l'ancienne table proprement
        df.to_sql(
            name=target_table,
            con=engine,
            if_exists="replace", 
            index=True,           
            method="multi"       
        )

        print(f"✅ Table '{target_table}' sauvegardée dans MySQL")

    except Exception as e:
        print(f"❌ Erreur SQL : {e}")