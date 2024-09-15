FROM python:3.10.12-bullseye

RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev

RUN sqlite3 --version

WORKDIR /code

COPY . /code/

ENV PATH="/code:$PATH"

COPY ./requirements.txt ./

RUN apt-get -y update \
    && apt-get -y install --no-install-recommends curl \
    && pip3 install --no-cache --upgrade pip setuptools \
    && pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN apt-get install -y sqlite3

COPY . .

COPY bin/* /code/bin/

CMD ["bash", "bin/start.sh"]