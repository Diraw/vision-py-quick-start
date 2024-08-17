# Use the official Python image as the base image
FROM python:3.11

# Install necessary libraries
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Set the working directory in the container
WORKDIR /app

# Copy the application files into the working directory
COPY . /app

# Install the application dependencies
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Expose the port that the Flask app runs on
EXPOSE 5000

# Set the FLASK_APP environment variable
ENV FLASK_APP=app.py

# Define the entry point for the container
CMD ["flask", "run", "--host=0.0.0.0"]
