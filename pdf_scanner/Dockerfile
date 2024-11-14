FROM python:3.11-slim

# Install dependencies
RUN pip install --no-cache-dir pypdf flask gunicorn

# Copy the application code
COPY . /app
WORKDIR /app

# Expose the port
EXPOSE 8080

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]