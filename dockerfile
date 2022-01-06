FROM ubuntu

RUN mkdir /GustelBOT/

RUN apt-get update && apt-get upgrade -y
RUN apt-get install ffmpeg -y
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y
RUN pip install discord.py
RUN pip install praw
RUN pip install PyNaCl
RUN pip install google-api-python-client
RUN pip install google-auth-oauthlib

#WORKDIR /GustelBOT/

CMD [ "python3", "/GustelBOT/GustelBOT/GustelBOT.py" ]
#ENTRYPOINT ["tail", "-f", "/dev/null"]

COPY ./GustelBOT/ /GustelBOT/
