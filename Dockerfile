# Use the official Python base image with Python 3.10
FROM python:3.10-slim

# # Install firefox
# RUN apt-get update                             \
#  && apt-get install -y --no-install-recommends \
#     ca-certificates curl firefox-esr           \
#  && rm -fr /var/lib/apt/lists/*                \
#  && curl -L https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz | tar xz -C /usr/local/bin 

## install dependencies
RUN apt update && apt-get install libnss3 libatk-bridge2.0-0 libcups2 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libxkbcommon0 libpango-1.0-0 libcairo2 libasound2 -y

WORKDIR /app

# Install the Python dependencies
COPY setup.py ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir . 

# chromium for kaleido
RUN plotly_get_chrome -y

# Copy the required files
COPY main.py .env ./
COPY services ./services
COPY routers ./routers
COPY utils ./utils

# Run the main.py script
CMD ["python3", "main.py"]
