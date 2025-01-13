# Use the official Python image as the base image
FROM --platform=$BUILDPLATFORM python:3.13.1-slim-bookworm

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose port 8501 for the Streamlit application
EXPOSE 8501

# Run the Streamlit application
CMD ["streamlit", "run", "main.py"]