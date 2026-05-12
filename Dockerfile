FROM python:3.10-slim

WORKDIR /app

# install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# copy project
COPY . .

# upgrade pip
RUN pip install --upgrade pip

# install python deps
RUN pip install --no-cache-dir -r requirements.txt

# Render port
ENV PORT=10000

EXPOSE 10000

# IMPORTANT: use PORT env (safer)
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:$PORT app:app"]
