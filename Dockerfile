# Use the official Python image as the base image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the application files into the working directory
COPY . /app

# Install the application dependencies
RUN pip install -r requirements.txt

# Expose the port that the Flask app runs on
EXPOSE 5000

# Set the FLASK_APP environment variable
ENV FLASK_APP=app.py

# Define the entry point for the container
CMD ["python", "app.py"]
