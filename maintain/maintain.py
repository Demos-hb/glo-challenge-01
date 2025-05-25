from google.cloud import bigquery
from datetime import datetime

# Configura tus valores aquí
PROJECT_ID = "iter-data-storage-pv-uat"
DATASET_ID = "temp"
BUCKET_NAME_INPUT = "demo-input-hb"
BUCKET_NAME_BACKUP = "demo-backup-hb"  # Asegúrate de que este bucket exista

# Archivos CSV y sus esquemas
CSV_FILES = {
    "hired_employees": {
        "file": "hired_employees.csv",
        "schema": [
            bigquery.SchemaField("id", "INT64", mode="NULLABLE"),
            bigquery.SchemaField("name", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("datetime", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField("department_id", "INT64", mode="NULLABLE"),
            bigquery.SchemaField("job_id", "INT64", mode="NULLABLE")
        ]
    },

    "departments": {
        "file": "departments.csv",
        "schema": [
            bigquery.SchemaField("id", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("department", "STRING", mode="NULLABLE"),
        ],
    },
    "jobs": {
        "file": "jobs.csv",
        "schema": [
            bigquery.SchemaField("id", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("job", "STRING", mode="NULLABLE"),
        ],
    },
}

def load_csv_to_bigquery(table_name, file_name, schema):
    client = bigquery.Client(project=PROJECT_ID)
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
    uri = f"gs://{BUCKET_NAME_INPUT}/{file_name}"

    job_config = bigquery.LoadJobConfig(
        schema=schema,
        skip_leading_rows=1,
        source_format=bigquery.SourceFormat.CSV,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        allow_quoted_newlines=True,
        ignore_unknown_values=True
    )

    print(f"Loading {file_name} into {table_id}...")
    load_job = client.load_table_from_uri(uri, table_id, job_config=job_config)
    load_job.result()  # Espera a que termine

    table = client.get_table(table_id)
    print(f"Loaded {table.num_rows} rows into {table_id}.")

def load_data():
    for table, config in CSV_FILES.items():
        load_csv_to_bigquery(table, config["file"], config["schema"])

def backup_table(table_name):
    client = bigquery.Client(project=PROJECT_ID)
    today = datetime.today().strftime('%Y-%m-%d')
    uri = f"gs://{BUCKET_NAME_BACKUP}/{table_name}/{table_name}_{today}.avro"

    job_config = bigquery.ExtractJobConfig(destination_format="AVRO")
    extract_job = client.extract_table(
        f"{PROJECT_ID}.{DATASET_ID}.{table_name}",
        uri,
        job_config=job_config
    )
    extract_job.result()
    print(f"Backed up table {table_name} to {uri}")

def backup():
    for table in CSV_FILES.keys():
        backup_table(table)
    print("Backup complete")

def restore_table(table_name, date):
    client = bigquery.Client(project=PROJECT_ID)
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
    uri = f"gs://{BUCKET_NAME_BACKUP}/{table_name}/{table_name}_{date}.avro"

    job_config = bigquery.LoadJobConfig(
        source_format="AVRO",
        write_disposition="WRITE_TRUNCATE"
    )

    load_job = client.load_table_from_uri(uri, table_id, job_config=job_config)
    load_job.result()
    print(f"Restored table {table_name} from {uri}")

def restore_all(date):
    for table in CSV_FILES.keys():
        restore_table(table, date)
    print("Restore complete")

if __name__ == "__main__":
    # Descomenta según la operación deseada
    load_data()
    #backup()
    #restore_all("2025-05-24")  # Asegúrate de usar la fecha correcta
    pass
