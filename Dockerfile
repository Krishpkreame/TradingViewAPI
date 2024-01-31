FROM python:3.11.4-slim

WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt

COPY ./app.py /app/

EXPOSE 5000

# Add required environment variables

# ENV SELENIUM_URL 
# ENV CMC_USERNAME 
# ENV CMC_PASSWORD 
# ENV MYSQL_DB1_JSON_CONN 


CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--with-threads"]