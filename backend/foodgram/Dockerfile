FROM python:3.8

WORKDIR /app

COPY . .

RUN apt update

RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]