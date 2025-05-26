from google.cloud import bigquery
from datetime import datetime

class BigQueryDataManager:
    def __init__(self, project_id, dataset_id, bucket_input, bucket_backup):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.bucket_input = bucket_input
        self.bucket_backup = bucket_backup
        self.client = bigquery.Client(project=project_id)

        self.csv_files = {
            "hired_employees": {
                "file": "hired_employees.csv",
                "schema": [
                    bigquery.SchemaField("id", "INT64", mode="NULLABLE"),
                    bigquery.SchemaField("name", "STRING", mode="NULLABLE"),
                    bigquery.SchemaField("datetime", "TIMESTAMP", mode="NULLABLE"),
                    bigquery.SchemaField("department_id", "INT64", mode="NULLABLE"),
                    bigquery.SchemaField("job_id", "INT64", mode="NULLABLE"),
                ],
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

    def load_csv_to_bigquery(self, table_name, file_name, schema):
        table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
        uri = f"gs://{self.bucket_input}/{file_name}"

        job_config = bigquery.LoadJobConfig(
            schema=schema,
            skip_leading_rows=1,
            source_format=bigquery.SourceFormat.CSV,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            allow_quoted_newlines=True,
            ignore_unknown_values=True,
            autodetect=False,
        )

        print(f"Loading {file_name} into {table_id}...")
        load_job = self.client.load_table_from_uri(uri, table_id, job_config=job_config)
        load_job.result()

        table = self.client.get_table(table_id)
        print(f"Loaded {table.num_rows} rows into {table_id}.")

    def load_data(self):
        for table, config in self.csv_files.items():
            self.load_csv_to_bigquery(table, config["file"], config["schema"])

    def backup_table(self, table_name):
        today = datetime.today().strftime('%Y-%m-%d')
        uri = f"gs://{self.bucket_backup}/{table_name}/{table_name}_{today}.avro"

        job_config = bigquery.ExtractJobConfig(destination_format="AVRO")
        extract_job = self.client.extract_table(
            f"{self.project_id}.{self.dataset_id}.{table_name}",
            uri,
            job_config=job_config
        )
        extract_job.result()
        print(f"Backed up table {table_name} to {uri}")

    def backup_all(self):
        for table in self.csv_files.keys():
            self.backup_table(table)
        print("Backup complete")
        return "Backup complete"

    def restore_table(self, table_name, date):
        table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
        uri = f"gs://{self.bucket_backup}/{table_name}/{table_name}_{date}.avro"

        job_config = bigquery.LoadJobConfig(
            source_format="AVRO",
            write_disposition="WRITE_TRUNCATE"
        )

        load_job = self.client.load_table_from_uri(uri, table_id, job_config=job_config)
        load_job.result()
        print(f"Restored table {table_name} from {uri}")

    def restore_all(self, date):
        for table in self.csv_files.keys():
            self.restore_table(table, date)
        print("Restore complete")

