# Use the official Python image from Docker Hub
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the containers
COPY requirements.txt /app/

# Install dependencies from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app/

# Expose the port the app will run on (Django default is 8000)
EXPOSE 8000

# Set environment variable to specify Django is in production mode s(optional)
# ENV DJANGO_SETTINGS_MODULE=your_project_name.settings.production

# Set the entrypoint for the container to start Django server when the container is run
CMD ["bash", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]