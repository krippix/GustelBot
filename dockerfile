FROM python:3

WORKDIR /GustelBot/

COPY ./bot ./bot
COPY ./data ./dataf
COPY ./requirements.txt ./

RUN apt update -y
RUN apt install ffmpeg -y
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "/GustelBot/bot/GustelBot.py" ]
