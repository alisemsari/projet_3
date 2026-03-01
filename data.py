import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st


# CONFIGURATION BASE DE DONNEES


# Informations de connexion MySQL

#USER = "root"
#PASSWORD = ""
#HOST = "localhost"
#PORT = "3306"
#DB_NAME = "wild_finance"
#USER = "avnadmin"
#PASSWORD = "AVNS_NvUql07Q0nHz_M4gXQm"   
#HOST = "mysql-36c8d2f2-siamak-5e08.j.aivencloud.com"
#PORT = "16144"
#DB_NAME = "defaultdb"
db_config = st.secrets["mysql"]

USER = db_config["user"]
PASSWORD = db_config["password"]
HOST = db_config["host"]
PORT = db_config["port"]
DB_NAME = db_config["database"]


# Création de l'URL de connexion SQLAlchemy
# Format :
# mysql+pymysql://user:password@host:port/database
connection_url = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

# Création du moteur SQLAlchemy
# echo=False = désactive les logs SQL
#engine = create_engine(connection_url, echo=False)
engine = create_engine(
    connection_url, 
    echo=False, 
    connect_args={"ssl": {"fake_config": "True"}} # Utilise la config SSL par défaut du système
)



# FONCTION : SAUVEGARDE DATAFRAME


def save_to_mysql(df, table_name):
    """
    Sauvegarde un DataFrame pandas dans une base MySQL.

    Cette fonction est une étape clé du pipeline ETL :
    - Extract : données collectées
    - Transform : données nettoyées
    - Load : sauvegarde en base SQL

    Paramètres
    ----------
    df : pandas.DataFrame
        Données à sauvegarder

    table_name : str
        Nom de la table SQL
    """

    try:

        # Nettoyage du nom de table
        # évite erreurs SQL
        target_table = table_name.lower().strip()

        # Nom de la colonne index
        # Important pour garder la date
        df.index.name = "Date"

        # Suppression de la table existante
        # Evite conflits de structure
        with engine.connect() as conn:
            #conn.execute(text(f"DROP TABLE IF EXISTS `{target_table}`"))

        # Sauvegarde du DataFrame en SQL
         df.to_sql(
            name=target_table,
            con=engine,
            if_exists="replace",  # remplace la table
            index=True,           # sauvegarde l'index
            method="multi"       # insertion plus rapide
        )

        print(f"✅ Table '{target_table}' sauvegardée dans MySQL")

    except Exception as e:

        # Gestion des erreurs
        print(f"❌ Erreur SQL : {e}")
