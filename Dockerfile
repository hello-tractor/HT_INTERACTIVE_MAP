# Set base image (host OS)
FROM python:3.10-slim-bullseye
# By default, listen on port 5000
EXPOSE 5000/tcp
# Set the working directory in the container
WORKDIR /app
# Copy the dependencies file to the working directory
COPY requirements.txt .
# Install any dependencies
RUN pip install -r requirements.txt
# Copy the content of the local src directory to the working directory
COPY . ./
# run the flask app using gunicorn
CMD ["gunicorn", "--timeout", "300", "app:app"]