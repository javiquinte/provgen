# our base image
FROM python:3.6-onbuild

# Set the working directory to /app
WORKDIR /provgen

# Copy the current directory contents into the container at /app
ADD . /provgen

# Install any needed packages specified in requirements.txt
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

# specify the port number the container should expose
EXPOSE 8000

# run the application
CMD ["python3.6", "./provgen.py"]