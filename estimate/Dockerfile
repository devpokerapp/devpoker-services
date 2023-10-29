FROM python:3.11.6-alpine

WORKDIR /app

ENV PYTHONPATH=/app/src

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD [ "sh", "entrypoint.sh" ]
