FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install nginx
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

COPY . .

# Make sure upload dir exists
RUN mkdir -p uploads

# Expose ports
EXPOSE 8000
EXPOSE 8501

RUN chmod +x start.sh

CMD ["./start.sh"]
