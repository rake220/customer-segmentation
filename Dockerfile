# Use official Python image as base
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port your FastAPI app uses
EXPOSE 8080

# Start FastAPI with uvicorn on container start
CMD ["uvicorn", "main1:app", "--host", "0.0.0.0", "--port", "8080"]
