FROM python:3.11.4-slim

WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt

EXPOSE 5000

# Add required environment variables
ENV SELENIUM_URL 'http://127.0.0.1:4444/wd/hub'
ENV DB_CONN_STR 'mongodb://mongoadmin:password@192.168.86.29:27017/'

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--with-threads"]
