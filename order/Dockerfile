FROM python:3.10-slim  

WORKDIR /app  

RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev && rm -rf /var/lib/apt/lists/*  

COPY . .  

RUN pip install Flask  

EXPOSE 5002  

CMD ["python", "app.py"]


