# 📁 File: backend/Dockerfile
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all backend files into the container
COPY . /app

# Install FastAPI dependencies including python-multipart for file uploads
RUN pip install fastapi uvicorn sqlalchemy python-multipart

# Expose the backend port
EXPOSE 8000

# Run the FastAPI app using Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

