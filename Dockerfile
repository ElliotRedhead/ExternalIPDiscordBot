FROM python:3

ADD externalipdiscordbot.py /
ADD requirements.txt /
ADD .env /

RUN pip install -r requirements.txt

CMD ["python", "externalipdiscordbot.py"]
