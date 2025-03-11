from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from sqlalchemy import create_engine, text
import boto3
import io
import pandas as pd
import os
from typing import Optional

# --------------------------------------------------------------------------
# 1️⃣ INITIALISATION DE L'API FASTAPI
# --------------------------------------------------------------------------

app = FastAPI()

# --------------------------------------------------------------------------
# 2️⃣ CONFIGURATION DES SOURCES DE DONNÉES
# --------------------------------------------------------------------------

# 🔹 Configuration S3 (Bronze)
S3_BUCKET = "my-bucket-datalake-2025"  # Remplacez par le bon nom de votre bucket S3
AWS_REGION = "eu-west-3"  # Changez selon votre région AWS
s3_client = boto3.client("s3")

# 🔹 Configuration MySQL (Silver)
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "votre_mot_de_passe"
MYSQL_DB = "projet_datalake"
engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}")

# 🔹 Configuration MongoDB (Gold)
MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "wine_gold"
MONGO_COLLECTION = "wine_collection"
mongo_client = MongoClient(MONGO_HOST, MONGO_PORT)
mongo_db = mongo_client[MONGO_DB]
mongo_collection = mongo_db[MONGO_COLLECTION]

# --------------------------------------------------------------------------
# 3️⃣ ROUTES DE L'API
# --------------------------------------------------------------------------

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Wine Quality Data Lake"}

# ==========================
# 1️⃣ Endpoint /raw (S3)
# ==========================
@app.get("/raw/{filename}")
def get_raw_data(filename: str):
    """
    Récupère un fichier brut depuis la couche Bronze (S3).
    """
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=filename)
        content = response["Body"].read()
        df = pd.read_csv(io.BytesIO(content), sep=";")
        return {"filename": filename, "data": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Fichier {filename} introuvable sur S3: {str(e)}")

# ==========================
# 2️⃣ Endpoint /staging (MySQL)
# ==========================
@app.get("/staging")
def get_staging_data(limit: int = 10):
    """
    Récupère les données de la couche Silver (staging) depuis MySQL.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text(f"SELECT * FROM wine_data LIMIT {limit}"))
            data = [dict(row._mapping) for row in result]
        return {"source": "MySQL (Staging)", "count": len(data), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur MySQL : {str(e)}")

# ==========================
# 3️⃣ Endpoint /curated (MongoDB)
# ==========================
@app.get("/curated")
def get_curated_data(limit: int = 10):
    """
    Récupère les données enrichies de la couche Gold (MongoDB).
    """
    try:
        results = list(mongo_collection.find({}, {"_id": 0}).limit(limit))
        return {"source": "MongoDB (Curated)", "count": len(results), "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur MongoDB : {str(e)}")

# ==========================
# 4️⃣ Endpoint /wines (MongoDB)
# ==========================
@app.get("/wines")
def get_wines(
    wine_type: Optional[str] = None,
    quality_category: Optional[str] = None,
    limit: int = 10
):
    """
    Retourne la liste des vins (avec filtres éventuels sur wine_type et quality_category),
    limité par défaut à 10 résultats.
    """
    query = {}
    if wine_type:
        query["wine_type"] = wine_type
    if quality_category:
        query["quality_category"] = quality_category

    results = list(mongo_collection.find(query, {"_id": 0}).limit(limit))
    return {"count": len(results), "data": results}

# ==========================
# 5️⃣ Endpoint /wines/stats (MongoDB)
# ==========================
@app.get("/wines/stats")
def get_wines_stats():
    """
    Exemple d'endpoint pour obtenir des statistiques simples 
    (moyenne d'alcool, nombre de vins) groupées par type de vin.
    """
    pipeline = [
        {
            "$group": {
                "_id": "$wine_type",
                "avg_alcohol": {"$avg": "$alcohol"},
                "count": {"$sum": 1}
            }
        }
    ]
    agg_results = list(mongo_collection.aggregate(pipeline))
    return {"stats": agg_results}


# ==========================
# Endpoint /ingest (MongoDB)
# ==========================
@app.post("/ingest")
def ingest_data(data: dict):
    """
    Endpoint pour recevoir de nouvelles données et les envoyer dans le pipeline.
    """
    try:
        start_time = time.time()

        # 1. Enregistrement dans S3 (Raw)
        filename = f"new_data_{int(time.time())}.json"
        s3_client.put_object(Bucket=S3_BUCKET, Key=filename, Body=json.dumps(data))

        # 2. Transformation et insertion dans MySQL (Staging)
        df = pd.DataFrame([data])
        df.to_sql("wine_data", con=engine, if_exists="append", index=False)

        # 3. Enrichissement et insertion dans MongoDB (Curated)
        data["quality_category"] = "bonne" if data["quality"] >= 7 else "moyenne" if data["quality"] >= 5 else "mauvaise"
        mongo_collection.insert_one(data)

        end_time = time.time()
        return {"message": "Data ingested successfully", "processing_time": f"{end_time - start_time:.2f} sec"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'ingestion : {str(e)}")



# ==========================
# Endpoint /ingest_fast 
# ==========================
@app.post("/ingest_fast")
def ingest_fast_data(data: list[dict]):
    """
    Ingestion optimisée (batch insertions).
    """
    try:
        start_time = time.time()

        # Enregistrement dans S3
        for record in data:
            s3_client.put_object(Bucket=S3_BUCKET, Key=f"fast_data_{int(time.time())}.json", Body=json.dumps(record))

        # Insertion en batch dans MySQL
        df = pd.DataFrame(data)
        df.to_sql("wine_data", con=engine, if_exists="append", index=False, method="multi")

        # Insertion en batch dans MongoDB
        mongo_collection.insert_many(data)

        end_time = time.time()
        return {"message": "Fast ingestion complete", "processing_time": f"{end_time - start_time:.2f} sec"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur ingestion rapide : {str(e)}")
