# GustelBot
My private Discord bot for experimenting.

## Ideas/ToDo
- (sounds) Display files as interactive embed in case more than 2000 characters are needet.
- React to said words (Is that even possible with pycord?)

## Administration
The admin commands of the bot can be used if the user fulfills one (or more) of the following conditions:
- role called "bot-admin"
- server administrator
- "manage channels" permission


## Commands

command     | description
----------- | :-------------
join        | joins users current channel
disconnect  | leaves current channel
play <name> | Searches for, and plays file with matching name. No parameter for random file.
stop        | Stops current playback
  
## Docker Installation
  
### Build
```
docker build . -t krippix/gustelbot
```
  
### docker-compose example
```
version: "3"

# https://github.com/krippix/GustelBOT
services:
  gustelbot:
    container_name: gustelbot
    image: krippix/gustelbot
    volumes:
      - '/<localPath>/data/:/GustelBOT/data/'
    restart: unless-stopped
```
