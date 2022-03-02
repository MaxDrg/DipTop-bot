FROM python:3.9.7-buster

WORKDIR /app

COPY requirements.txt /app

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "bot.py"]