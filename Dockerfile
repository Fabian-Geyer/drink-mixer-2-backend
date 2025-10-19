# start by pulling the python image
FROM python:3.8-alpine

WORKDIR /app

# Install build dependencies
RUN apk add build-base

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the application
RUN pip install --no-cache-dir .

# Set environment variables for Flask
ENV FLASK_APP=coma2.main
ENV FLASK_ENV=development
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5055

# Create volume mount point
VOLUME /data

# Initialize database and start Flask
# Note: Using init_db.py instead of create_tables.py to avoid circular import issues
CMD ["sh", "-c", "python init_db.py && flask run --host=0.0.0.0 --port=5055"]