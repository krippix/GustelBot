FROM python:3.11-bookworm

WORKDIR /GustelBot/

RUN apt-get update && apt-get install ffmpeg -y

COPY ./requirements.txt ./
COPY ./gustelbot ./gustelbot
COPY ./data ./data

RUN pip install -r requirements.txt

CMD [ "python", "-m", "gustelbot" ]