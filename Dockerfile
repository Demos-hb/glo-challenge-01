FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

# Cloud Run usa el puerto 8080 por defecto
ENV PORT=8080

CMD ["python", "api.main:app"]