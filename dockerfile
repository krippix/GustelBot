FROM python:3.11-bookworm

WORKDIR /GustelBot/

COPY ./bot ./bot
COPY ./data ./dataf
COPY ./requirements.txt ./

RUN apt-get update -y
RUN apt-get install ffmpeg -y
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "/GustelBot/bot/GustelBot.py" ]
