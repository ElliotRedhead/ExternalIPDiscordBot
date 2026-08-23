FROM python:3.14-slim

LABEL com.centurylinklabs.watchtower.enable="false"

WORKDIR /app
COPY externalipdiscordbot.py requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN useradd --create-home bot && chown bot /app
USER bot

CMD ["python", "externalipdiscordbot.py"]
