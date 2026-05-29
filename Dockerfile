FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080
ENV PYTHONUNBUFFERED=1

# Run the main script directly. If you prefer module style, change back to: ["python","-m","main"]
CMD ["python", "main.py"]