FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY security_exporter.py .

CMD ["python3", "security_exporter.py"]