# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn
RUN pip install gunicorn

# Copy the rest of the application code
COPY . .

# Make port 5001 available for the app
EXPOSE 5001

# Run the app
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "paymentservice:app"]