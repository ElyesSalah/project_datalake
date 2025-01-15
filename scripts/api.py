from fastapi import FastAPI
from pymongo import MongoClient
from typing import Optional

# 1) Initialisation FastAPI
app = FastAPI()

# 2) Connexion à MongoDB (Gold)
client = MongoClient("mongodb://localhost:27017/")
db = client["wine_gold"]                # Base MongoDB
collection = db["wine_collection"]      # Collection enrichie

@app.get("/")
def read_root():
    return {"message": "Welcome to Wine Quality API (couche Gold)"}

@app.get("/wines")
def get_wines(
    wine_type: Optional[str] = None,
    quality_category: Optional[str] = None,
    limit: int = 10
):
    """
    Retourne la liste des vins (avec filtre éventuel sur wine_type et quality_category),
    limité par défaut à 10 résultats.
    """
    query = {}
    if wine_type:
        query["wine_type"] = wine_type
    if quality_category:
        query["quality_category"] = quality_category

    results = list(collection.find(query, {"_id": 0}).limit(limit))
    return {"count": len(results), "data": results}

@app.get("/wines/stats")
def get_wines_stats():
    """
    Exemple d'endpoint pour obtenir des stats simples 
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
    agg_results = list(collection.aggregate(pipeline))
    return {"stats": agg_results}
