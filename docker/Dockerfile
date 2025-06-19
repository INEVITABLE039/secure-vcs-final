FROM python:3.10-slim

# Set base working directory
WORKDIR /app

# Copy entire src folder into container
COPY ./src /app/src

# Move into the actual code directory
WORKDIR /app/src

# Install required packages
RUN pip install flask werkzeug

# Run your app from /app/src/app.py
CMD ["python", "app.py"]

