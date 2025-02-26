FROM python:3.13

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]