FROM python:3.14-slim

ADD externalipdiscordbot.py /
ADD requirements.txt /

RUN pip install -r requirements.txt

CMD ["python", "externalipdiscordbot.py"]
