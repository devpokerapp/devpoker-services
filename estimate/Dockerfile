FROM python:3.11.6-alpine

WORKDIR /app

ENV PYTHON_PATH=/app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD [ "nameko", "run", "src.main" ]
