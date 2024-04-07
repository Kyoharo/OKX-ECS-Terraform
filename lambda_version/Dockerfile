
# Use a lightweight base image
FROM python:3.9-slim

# Set the working directory (can be overridden in Lambda GUI)
WORKDIR /app

# Copy requirements file
COPY requirements.txt requirements.txt

# Install dependencies without caching 
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY ./app .

# Entrypoint for Lambda to invoke (can be overridden in Lambda GUI)
ENTRYPOINT ["python"]

# Command arguments for the entrypoint (can be overridden in Lambda GUI)
CMD ["main.py"]
