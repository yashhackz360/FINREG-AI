# [cite_start]Base image with Python [cite: 1]
FROM python:3.12-slim

# [cite_start]Set working directory [cite: 1]
WORKDIR /app

# [cite_start]Install system dependencies required by scientific libs [cite: 1]
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# [cite_start]Copy requirements and install them [cite: 1]
COPY requirements.txt .

# Install PyTorch and its CPU dependencies first from the official index
RUN pip install torch==2.3.1 torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# [cite_start]Install the rest of the dependencies [cite: 2]
RUN pip install --no-cache-dir -r requirements.txt

# [cite_start]Copy entire project into container [cite: 1]
COPY . .

# [cite_start]Default command (overridden by docker-compose.yml) [cite: 3]
CMD ["python", "scripts/01_ingest_data.py"]