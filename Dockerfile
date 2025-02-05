# Use a Python base image (non-slim can be more complete)
FROM python:3.11

# Install system dependencies, including Tesseract OCR
RUN apt-get update && apt-get install -y tesseract-ocr && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy your requirements file and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . /app

# Expose the port your Flask app will run on
EXPOSE 5000

# Run your app
CMD ["python", "app.py"]

RUN which tesseract && tesseract --version
