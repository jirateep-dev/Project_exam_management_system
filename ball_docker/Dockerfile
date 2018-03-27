FROM python:3.6-slim

WORKDIR /data

RUN set -ex && apt-get update -y && apt-get -y install libmysqlclient-dev \
				python3-dev libevent-dev build-essential

COPY requirements.txt /data/requirements.txt

RUN pip install -r requirements.txt

COPY . /project

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]