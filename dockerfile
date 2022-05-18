FROM python:3

WORKDIR /GustelBOT/

COPY ./bot ./
COPY ./requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "/bot/GustelBot.py"]