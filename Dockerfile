# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory to /app
WORKDIR /server

# Copy the current directory contents into the container at /app
COPY . /server

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Install additional packages
RUN pip install google-api-python-client

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "server.py"]
