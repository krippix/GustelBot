FROM python:3.11-bookworm

WORKDIR /GustelBot/

RUN apt-get update && apt-get install ffmpeg -y

COPY ./requirements.txt ./
RUN pip install -r requirements.txt

COPY ./bot ./bot
COPY ./data ./data

CMD [ "python", "/GustelBot/bot/GustelBot.py" ]