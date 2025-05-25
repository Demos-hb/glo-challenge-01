import os
import json
import uuid
from flask import Flask, request, jsonify
from pydantic import BaseModel
from typing import List, Optional
from google.cloud import bigquery
from google.cloud import storage
from datetime import datetime

venv_project_id = os.getenv("GCP_PROJECT_ID")
#bucket_name = os.getenv("GCS_BUCKET_NAME") 

app = Flask(__name__)

# Instancia del cliente de BigQuery y Storage
client = bigquery.Client()
storage_client = storage.Client()

project_id = "iter-data-storage-pv-uat"
dataset_id = "temp"  # Ajusta según corresponda
bucket_name = "demo-log-hb"  # Ajusta según corresponda

# -------------------------------
# Modelos de entrada
# -------------------------------

class HiredEmployee(BaseModel):
    id: Optional[int]
    name: Optional[str]
    datetime: Optional[datetime]
    department_id: Optional[int]
    job_id: Optional[int]

class Department(BaseModel):
    id: Optional[int]
    department: Optional[str]

class Job(BaseModel):
    id: Optional[int]
    job: Optional[str]

# -------------------------------
# Funciones auxiliares
# -------------------------------

def is_valid(record: dict) -> bool:
    return all(value is not None for value in record.values())
    
def upload_to_gcs(data: List[dict], prefix: str):
    now = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    file_name = f"{prefix}_invalid_{now}_{uuid.uuid4().hex[:8]}.json"
    blob_path = f"log/{file_name}"  # Directorio 'log/'
    blob = storage_client.bucket(bucket_name).blob(blob_path)
    blob.upload_from_string(json.dumps(data), content_type="application/json")
    return blob_path

def insert_rows_to_bq(table_name: str, rows: List[dict]):
    table_ref = f"{project_id}.{dataset_id}.{table_name}"
    errors = client.insert_rows_json(table_ref, rows)
    if errors:
        raise Exception(f"BigQuery errors: {errors}")
    return {"message": f"{len(rows)} rows inserted into {table_name}"}

def process_records(data: List[BaseModel], prefix: str, table_name: str, datetime_field: Optional[str] = None):
    rows = [record.dict() for record in data]

    # Si hay un campo datetime, convertirlo a string ISO para serializar
    if datetime_field:
        for row in rows:
            if row.get(datetime_field) is not None:
                row[datetime_field] = row[datetime_field].isoformat()

    valid_records = [r for r in rows if is_valid(r)]
    invalid_records = [r for r in rows if not is_valid(r)]

    response = {}

    if valid_records:
        insert_rows_to_bq(table_name, valid_records)
        response["inserted"] = len(valid_records)

    if invalid_records:
        file_path = upload_to_gcs(invalid_records, prefix)
        response["invalid"] = len(invalid_records)
        response["invalid_gcs_path"] = f"gs://{bucket_name}/{file_path}"

    return response

# -------------------------------
# Endpoints
# -------------------------------

@app.route('/hired_employees', methods=['POST'])
def upload_hired_employees():
    try:
        data = request.get_json()

        if not isinstance(data, list):
            return jsonify({"error": "Request body must be a JSON array"}), 400
        if len(data) == 0:
            return jsonify({"error": "At least one record is required"}), 400
        if len(data) > 1000:
            return jsonify({"error": "Batch size limit exceeded (max 1000 records)"}), 400

        employees = [HiredEmployee(**item) for item in data]

        response = process_records(employees, "hired_employees", "hired_employees", datetime_field="datetime")

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/departments", methods=["POST"])
def upload_departments():
    try:
        data = request.get_json()

        if not isinstance(data, list):
            return jsonify({"error": "Request body must be a JSON array"}), 400
        if len(data) == 0:
            return jsonify({"error": "At least one record is required"}), 400
        if len(data) > 1000:
            return jsonify({"error": "Batch size limit exceeded (max 1000 records)"}), 400

        departments = [Department(**item) for item in data]

        response = process_records(departments, "departments", "departments")

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/jobs", methods=["POST"])
def upload_jobs():
    try:
        data = request.get_json()

        if not isinstance(data, list):
            return jsonify({"error": "Request body must be a JSON array"}), 400
        if len(data) == 0:
            return jsonify({"error": "At least one record is required"}), 400
        if len(data) > 1000:
            return jsonify({"error": "Batch size limit exceeded (max 1000 records)"}), 400

        jobs = [Job(**item) for item in data]

        response = process_records(jobs, "jobs", "jobs")

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------
# Run
# -------------------------------

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
