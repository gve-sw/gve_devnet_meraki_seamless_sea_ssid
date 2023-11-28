FROM python:3.11-slim-buster
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install -r requirements.txt
# Copy the current directory contents into the container at /app
COPY ./src/meraki_seamless_sea_ssid/ .
EXPOSE 8000
CMD ["python", "./app.py"]
