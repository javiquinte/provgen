# our base image
FROM python:3.6-onbuild

# specify the port number the container should expose
EXPOSE 8000

# run the application
CMD ["python3.6", "./provgen.py"]