FROM python:3.11.4-slim

WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt

COPY ./app.py /app/

EXPOSE 5000

# Add required environment variables

ENV SELENIUM_URL 'http://127.0.0.1:4444/wd/hub'
ENV MYSQL_DB1_JSON_CONN '{"host": "127.0.0.1", "user": "user", "password": "password", "database": "cmc_api"}'

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--with-threads"]
