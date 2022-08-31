# start by pulling the python image
FROM python:3.8-alpine

WORKDIR /app

# RUN apk update && apk add --no-cache postgresql-dev

COPY requirements.txt ./
RUN apk add build-base
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install --no-cache-dir .

VOLUME /data

CMD ["flask", "run", "--host=0.0.0.0"]