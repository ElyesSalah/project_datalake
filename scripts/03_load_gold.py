import pandas as pd
import sqlalchemy
from pymongo import MongoClient

# -------------------------------------------------------------------
# PARAMÈTRES / CONFIG
# -------------------------------------------------------------------
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "9852xywbaqtz"
MYSQL_DB = "projet_datalake"     # Schéma MySQL
MYSQL_TABLE = "wine_data"        # Table Silver

MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "wine_gold"           # Nom de la base MongoDB
MONGO_COLLECTION = "wine_collection"

# -------------------------------------------------------------------
# FONCTIONS UTILES
# -------------------------------------------------------------------
def quality_to_category(quality):
    """
    Transforme la note de 0-10 en catégorie :
    0-4 : "mauvaise", 5-6 : "moyenne", 7-10 : "bonne"
    """
    if quality <= 4:
        return "mauvaise"
    elif 5 <= quality <= 6:
        return "moyenne"
    else:
        return "bonne"

# -------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------
if __name__ == "__main__":
    print("=== [03_load_gold.py] DÉBUT DE L'EXÉCUTION ===")

    # 1) Connexion MySQL (Silver)
    engine_str = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    engine = sqlalchemy.create_engine(engine_str)

    # 2) Lecture de la table Silver (wine_data)
    print("[INFO] Lecture de la table MySQL (Silver) ...")
    df_silver = pd.read_sql_table(MYSQL_TABLE, con=engine)

    print(f"[INFO] Nombre de lignes lues : {len(df_silver)}")

    # 3) Enrichissement : ajout de "quality_category"
    print("[INFO] Enrichissement des données (catégorisation de la quality)...")
    df_silver["quality_category"] = df_silver["quality"].apply(quality_to_category)

    # 4) Connexion MongoDB (Gold)
    print("[INFO] Connexion à MongoDB ...")
    client = MongoClient(MONGO_HOST, MONGO_PORT)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]

    # 5) Conversion en liste de dictionnaires (compatible Mongo)
    data_dicts = df_silver.to_dict(orient="records")

    # 6) Insertion en MongoDB
    #    -> On peut faire un "collection.delete_many({})" si on veut d'abord vider la collection
    print("[INFO] Insertion des documents dans MongoDB (Gold)...")
    collection.insert_many(data_dicts)

    print(f"[OK] {len(data_dicts)} documents insérés dans la collection '{MONGO_COLLECTION}'.")
    print("=== [03_load_gold.py] FIN DE L'EXÉCUTION ===")
