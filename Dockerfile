# syntax=docker/dockerfile:1
FROM python:3.11-rc
WORKDIR /code
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["python", "app.py"]
