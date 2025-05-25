import os
from flask import Flask, request, jsonify
from pydantic import BaseModel
from typing import List, Optional
from google.cloud import bigquery

venv_project_id = os.getenv("GCP_PROJECT_ID")

app = Flask(__name__)

# Instancia del cliente de BigQuery
client = bigquery.Client()
project_id = venv_project_id
#project_id = ""
dataset_id = "temp"  # Ajusta según corresponda

# -------------------------------
# Modelos de entrada
# -------------------------------

class HiredEmployee(BaseModel):
    id: Optional[int]
    name: Optional[str]
    datetime: Optional[str]
    department_id: Optional[int]
    job_id: Optional[int]

class Department(BaseModel):
    id: Optional[int]
    department: Optional[str]

class Job(BaseModel):
    id: Optional[int]
    job: Optional[str]

# -------------------------------
# Función de inserción
# -------------------------------

def insert_rows_to_bq(table_name: str, rows: List[dict]):
    table_ref = f"{project_id}.{dataset_id}.{table_name}"
    errors = client.insert_rows_json(table_ref, rows)
    if errors:
        raise Exception(f"BigQuery errors: {errors}")
    return {"message": f"{len(rows)} rows inserted into {table_name}"}

# -------------------------------
# Endpoints
# -------------------------------

@app.route('/hired_employees', methods=['POST'])
def upload_hired_employees():
    try:
        data = request.get_json()
        employees = [HiredEmployee(**item) for item in data]
        rows = [employee.dict() for employee in employees]
        insert_rows_to_bq("hired_employees", rows)
        return jsonify({"message": "Hired employees uploaded successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/departments", methods=["POST"])
def upload_departments():
    try:
        data = request.get_json()
        departments = [Department(**item) for item in data]
        rows = [dept.dict() for dept in departments]
        insert_rows_to_bq("departments", rows)
        return jsonify({"message": "Departments data uploaded successfully"}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/jobs", methods=["POST"])
def upload_jobs():
    try:
        data = request.get_json()
        jobs = [Job(**item) for item in data]
        rows = [job.dict() for job in jobs]
        insert_rows_to_bq("jobs", rows)
        return jsonify({"message": "Jobs uploaded successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------
# Run
# -------------------------------

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
