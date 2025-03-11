import boto3
import os

def upload_to_s3(local_path, bucket_name, s3_path):
    s3_client = boto3.client('s3')
    s3_client.upload_file(local_path, bucket_name, s3_path)

if __name__ == "__main__":
    # Exemple d’utilisation
    bucket = "my-bucket-datalake-2025"
    files = ["winequality-red.csv", "winequality-white.csv", "winequality.names"]
    local_folder = "data/raw"

    for f in files:
        local_file = os.path.join(local_folder, f)
        upload_to_s3(local_file, bucket, f)
        print(f"Uploaded {local_file} to s3://{bucket}/{f}")
