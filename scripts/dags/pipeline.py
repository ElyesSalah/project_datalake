from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os

# Définition du DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'pipeline_datalake',
    default_args=default_args,
    description='Pipeline Airflow pour ingestion et transformation des données',
    schedule_interval='@daily',
    catchup=False,
)

# Définition des tâches
def ingest():
    os.system("python /opt/airflow/scripts/01_ingest.py")

def transform():
    os.system("python /opt/airflow/scripts/02_transform.py")

def load_gold():
    os.system("python /opt/airflow/scripts/03_load_gold.py")

task_ingest = PythonOperator(
    task_id='ingest_data',
    python_callable=ingest,
    dag=dag,
)

task_transform = PythonOperator(
    task_id='transform_data',
    python_callable=transform,
    dag=dag,
)

task_load = PythonOperator(
    task_id='load_gold_data',
    python_callable=load_gold,
    dag=dag,
)

# Dépendances entre les tâches
task_ingest >> task_transform >> task_load
