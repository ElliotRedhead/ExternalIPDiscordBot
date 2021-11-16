FROM python:3

ADD externalipdiscordbot.py /
ADD requirements.txt /
ADD .env /
ADD commands.json /

RUN pip install -r requirements.txt

CMD ["python", "externalipdiscordbot.py"]
