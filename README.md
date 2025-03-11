### 📌 **README Complet pour Déploiement et Utilisation du Projet Data Lake**  
🚀 Ce **README** détaille **chaque étape** pour **installer, configurer et exécuter** la solution **Data Lake** basée sur **S3, MySQL, MongoDB, Airflow et FastAPI**.  

---

## 📌 **1. Pré-requis**  
Avant de commencer, assure-toi d’avoir les applications suivantes installées :

✅ **Docker & Docker Compose** ([Installation](https://docs.docker.com/get-docker/))  
✅ **Python 3.8+** ([Installation](https://www.python.org/downloads/))  
✅ **MongoDB** ([Installation](https://www.mongodb.com/try/download/community))  
✅ **MySQL** ([Installation](https://dev.mysql.com/downloads/installer/))  
✅ **Git** ([Installation](https://git-scm.com/downloads))  

---

## 📌 **2. Cloner le projet et installer les dépendances**  
Clone le projet et installe les bibliothèques nécessaires :

```bash
git clone https://github.com/ElyesSalah/project_datalake.git
cd projet_datalake
```

Avec un environnement virtuel Python :
```bash
python -m venv venv
source venv/bin/activate  # Sur macOS/Linux
venv\Scripts\activate  # Sur Windows
```

Puis, installer les dépendances :
```bash
pip install -r requirements.txt
```

---

## 📌 **3. Lancer les services (MySQL, MongoDB, Airflow) avec Docker**
Le projet utilise **Docker Compose** pour démarrer les services automatiquement.

### 🛠 **Démarrer MySQL, MongoDB et Airflow**
```bash
docker-compose up -d
```
📌 **Ce que cela fait :**  
✅ Lance **PostgreSQL pour Airflow**  
✅ Démarre **Airflow (Scheduler, Webserver)**  
✅ Active **MongoDB**  

---

## 📌 **4. Vérifier et configurer Airflow**
Une fois lancé, ouvre **Airflow UI** et connecte-toi :

👉 **[http://localhost:8080](http://localhost:8080)**  
📌 **Identifiants :**
- **Utilisateur** : `admin`
- **Mot de passe** : `admin`

Vérifie que le DAG **`pipeline_datalake`** est bien listé.

---

## 📌 **5. Ajouter et exécuter un DAG Airflow**
Le pipeline d’Airflow est défini dans **`dags/pipeline.py`**. Il exécute trois tâches :
1. **`ingest_data`** → Récupère les données brutes.
2. **`transform_data`** → Nettoie et stocke dans MySQL.
3. **`load_gold_data`** → Enrichit et stocke dans MongoDB.

### **Activer le DAG**
1. Va dans l’interface Airflow.
2. Active **`pipeline_datalake`**.
3. Clique sur ▶️ **"Trigger DAG"** pour l’exécuter.

---

## 📌 **6. Vérifier les bases de données**
### **🔹 MySQL (Silver)**
Accède à **MySQL Workbench** ou via terminal :
```bash
mysql -u root -p
USE projet_datalake;
SELECT * FROM wine_data LIMIT 5;
```

### **🔹 MongoDB (Gold)**
Accède à **MongoDB Compass** ou via terminal :
```bash
mongo
use wine_gold
db.wine_collection.find().limit(5)
```

---

## 📌 **7. Lancer l’API FastAPI**
FastAPI expose plusieurs endpoints pour récupérer les données du **Data Lake**.

### **1️⃣ Démarrer l'API**
Dans le dossier du projet :
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### **2️⃣ Accéder aux données**
👉 **Swagger UI** : [http://localhost:8000/docs](http://localhost:8000/docs)

📌 **Exemples de requêtes API :**
```bash
# Obtenir les données brutes depuis S3
curl http://localhost:8000/raw/winequality-red.csv

# Obtenir les données MySQL (Silver)
curl http://localhost:8000/staging?limit=5

# Obtenir les données enrichies (MongoDB)
curl http://localhost:8000/curated?limit=5
```

---

## 📌 **8. Tester l’ensemble du pipeline**
Des tests unitaires sont disponibles dans **`tests/`**.

### **1️⃣ Tester les scripts indépendamment**
```bash
python scripts/01_ingest.py
python scripts/02_transform.py
python scripts/03_load_gold.py
```

### **2️⃣ Exécuter les tests unitaires**
```bash
pytest tests/
```
📌 Vérifie que tous les tests **passent avec succès** ✅.

---

## 📌 **9. Déploiement et utilisation en production**
Si tu veux **exécuter le projet en production**, voici quelques étapes recommandées :

### **1️⃣ Démarrer en mode production**
Utiliser `docker-compose.prod.yml` :
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### **2️⃣ Déployer l’API sur un serveur**
- Hébergement possible sur **AWS EC2, GCP, Azure**.
- Utilisation de **NGINX ou Traefik** pour exposer l’API FastAPI.

---

## 📌 **10. Résumé des commandes essentielles**
| **Action** | **Commande** |
|------------|-------------|
| **1. Cloner le projet** | `git clone https://github.com/votre-repo/projet_datalake.git` |
| **2. Installer les dépendances** | `pip install -r requirements.txt` |
| **3. Démarrer MySQL, MongoDB et Airflow** | `docker-compose up -d` |
| **4. Accéder à Airflow** | [http://localhost:8080](http://localhost:8080) |
| **5. Lancer l’API FastAPI** | `uvicorn api:app --host 0.0.0.0 --port 8000 --reload` |
| **6. Tester les endpoints API** | `curl http://localhost:8000/wines` |
| **7. Vérifier MySQL** | `mysql -u root -p` |
| **8. Vérifier MongoDB** | `mongo wine_gold` |
| **9. Exécuter les tests unitaires** | `pytest tests/` |

---

🚀 **Ton projet est maintenant bien structuré et prêt à être exécuté !**  
Dis-moi si tu veux ajouter quelque chose à la documentation ! 😊
