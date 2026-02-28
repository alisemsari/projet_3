import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st


# ==============================
# CONFIGURATION BASE DE DONNEES
# ==============================

db_config = st.secrets["mysql"]

USER = db_config["user"]
PASSWORD = db_config["password"]
HOST = db_config["host"]
PORT = db_config["port"]
DB_NAME = db_config["database"]

# URL connexion
connection_url = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

# ENGINE SQLAlchemy compatible AIVEN (SSL obligatoire)
engine = create_engine(
    connection_url,
    echo=True,  # 🔎 active les logs SQL
    connect_args={
        "ssl": {
            "ssl_mode": "REQUIRED"
        }
    }
)

# ==============================
# FONCTION SAUVEGARDE MYSQL
# ==============================

def save_to_mysql(df, table_name):

    try:
        target_table = table_name.lower().strip()

        # On garde la date
        df.index.name = "Date"

        # Sauvegarde en base
        df.to_sql(
            name=target_table,
            con=engine,
            if_exists="replace",
            index=True,
            method="multi"
        )

        print(f"✅ Table '{target_table}' sauvegardée")

        # Vérification insertion
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {target_table}"))
            count = result.scalar()
            print(f"📊 Nombre de lignes insérées : {count}")

    except Exception as e:
        print(f"❌ Erreur SQL : {e}")