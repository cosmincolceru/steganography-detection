FROM python:3.9-slim

WORKDIR /app

RUN pip install --no-cache-dir Flask==3.0.3

RUN pip install --no-cache-dir tensorflow==2.16.1

WORKDIR /app

COPY . /app

EXPOSE 5000

CMD ["python", "app.py"]
