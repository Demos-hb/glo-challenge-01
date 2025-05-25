import requests

BASE_URL = "http://localhost:8080"

# Datos de prueba para hired_employees
hired_employees_data = [
    {
        "id": 4535,
        "name": "Marcelo Gonzalez",
        "datetime": "2021-07-27T16:02:08Z",
        "department_id": 1,
        "job_id": 2
    },
    {
        "id": 4572,
        "name": "Lidia Mendez",
        "datetime": "2021-07-27T19:04:09Z",
        "department_id": 1,
        "job_id": 2
    }
]

# Datos de prueba para departments
departments_data = [
    {"id": 1, "department": "Supply Chain"},
    {"id": 2, "department": "Maintenance"},
    {"id": 3, "department": "Staff"}
]

# Datos de prueba para jobs
jobs_data = [
    {"id": 1, "job": "Recruiter"},
    {"id": 2, "job": "Manager"},
    {"id": 3, "job": "Analyst"}
]

def post_data(endpoint, data):
    url = f"{BASE_URL}/{endpoint}"
    response = requests.post(url, json=data)
    print(f"\nPOST {endpoint}")
    print(f"Status Code: {response.status_code}")
    print("Response:", response.json())

# Ejecutar pruebas
if __name__ == "__main__":
    post_data("departments", departments_data)
    post_data("jobs", jobs_data)
    post_data("hired_employees", hired_employees_data)
