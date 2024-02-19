FROM python:3.11.4-slim

WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt

EXPOSE 5000

# Set environment variables with docker run NOT IN DOCKERFILE

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--with-threads"]
