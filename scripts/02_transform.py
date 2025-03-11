import os
import io
import sys
import boto3
import pandas as pd
import sqlalchemy
from sqlalchemy.exc import SQLAlchemyError

# ----------------------------------------------------------------------------
# CONFIGURATION 
# ----------------------------------------------------------------------------

USE_S3 = True  # Passez à False si vous voulez lire en local (fallback)
BUCKET_NAME = "my-bucket-datalake-2025"

# Fichiers CSV dans S3 OU en local
FILES = {
    "winequality-red.csv": "red",
    "winequality-white.csv": "white"
}

# Chemin local si USE_S3 = False
LOCAL_RAW_PATH = "data/raw"

# Paramètres MySQL
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "9852xywbaqtz"  
MYSQL_DB = "projet_datalake"        # Schéma
TABLE_NAME = "wine_data"

# ----------------------------------------------------------------------------
# FONCTIONS UTILES
# ----------------------------------------------------------------------------

def get_csv_from_s3(bucket, file_key):
    """
    Lit un CSV sur S3 et retourne un DataFrame Pandas.
    """
    try:
        s3_client = boto3.client('s3')
        response = s3_client.get_object(Bucket=bucket, Key=file_key)
        # On lit le contenu binaire dans un buffer
        data = response['Body'].read()
        # Pandas lit le CSV avec séparateur ";" (cas Wine Quality)
        df = pd.read_csv(io.BytesIO(data), sep=";")
        return df
    except Exception as e:
        print(f"[ERREUR] Impossible de lire {file_key} sur S3 : {e}")
        sys.exit(1)


def get_csv_local(file_path):
    """
    Lit un CSV local et retourne un DataFrame Pandas.
    """
    try:
        df = pd.read_csv(file_path, sep=";")
        return df
    except FileNotFoundError:
        print(f"[ERREUR] Fichier introuvable : {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERREUR] Problème lors de la lecture du CSV local : {e}")
        sys.exit(1)


def preprocess_data(df, wine_type):
    """
    Applique les transformations de base :
    - Ajout de la colonne wine_type
    - Renommage des colonnes (remplacement des espaces par des underscores)
    - Gestion éventuelle des valeurs manquantes
    """
    df["wine_type"] = wine_type

    # Renommer les colonnes pour enlever les espaces
    df.columns = [col.replace(" ", "_") for col in df.columns]

    # Exemple : on peut remplir des NaN par la moyenne (si NaN, rare dans WineQuality)
    # for col in df.columns:
    #     if df[col].dtype in [float, int]:
    #         df[col].fillna(df[col].mean(), inplace=True)

    return df


def save_to_mysql(df, engine, table_name):
    """
    Sauvegarde le DataFrame dans MySQL (mode append).
    """
    try:
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists='append',
            index=False
        )
        print(f"[OK] {len(df)} lignes insérées dans la table '{table_name}'.")
    except SQLAlchemyError as e:
        print(f"[ERREUR] lors de l'insertion MySQL : {e}")
        sys.exit(1)


# ----------------------------------------------------------------------------
# MAIN 
# ----------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== [02_transform.py] DÉBUT DE L'EXÉCUTION ===")

    # 1) Connexion à MySQL (SQLAlchemy)
    engine_str = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    engine = sqlalchemy.create_engine(engine_str)

    # 2) Lecture des CSV (S3 ou local) et concaténation
    all_dfs = []
    for file_name, wine_type in FILES.items():
        if USE_S3:
            print(f"[INFO] Lecture de {file_name} depuis le bucket S3 '{BUCKET_NAME}'...")
            df_temp = get_csv_from_s3(BUCKET_NAME, file_name)
        else:
            local_file_path = os.path.join(LOCAL_RAW_PATH, file_name)
            print(f"[INFO] Lecture de {local_file_path} en local...")
            df_temp = get_csv_local(local_file_path)

        # Nettoyage et ajout de la colonne "wine_type"
        df_temp = preprocess_data(df_temp, wine_type)
        all_dfs.append(df_temp)

    # Concaténer en un seul DataFrame
    df_silver = pd.concat(all_dfs, ignore_index=True)

    # 3) Petit résumé exploratoire
    print("[INFO] Aperçu du DataFrame final :")
    print(df_silver.head(5))
    print("[INFO] Nombre de lignes / colonnes :", df_silver.shape)
    print("[INFO] Valeurs manquantes :")
    print(df_silver.isnull().sum())

    # 4) Insertion dans MySQL (couche Silver)
    print(f"[INFO] Insertion dans MySQL -> Schéma : {MYSQL_DB}, Table : {TABLE_NAME}")
    save_to_mysql(df_silver, engine, TABLE_NAME)

    print("=== [02_transform.py] FIN DE L'EXÉCUTION ===")
