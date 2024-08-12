FROM python:3.11-bookworm

WORKDIR /GustelBot/

RUN apt-get update && apt-get install ffmpeg -y

COPY ./requirements.txt ./
RUN pip install -r requirements.txt

COPY ./gustelbot ./gustelbot
COPY ./data ./data

CMD [ "python", "-m", "gustelbot" ]