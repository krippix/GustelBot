# GustelBOT
discord.py experiments. 

## Commands

command     | description
----------- | :-------------
join        | joins users current channel
disconnect  | leaves current channel
play <name> | Searches for, and plays file with matching name. No parameter for random file.
stop        | Stops current playback

## Configuration
- Save YouTube OAuth Token in /data/youtube/ as client_secret.json

## ToDo

  
## Installation Stuff
  
  ```
  docker build . -t krippix/gustelbot
  ```
  
```
version: "3"

# https://github.com/krippix/GustelBOT
services:
  gustelbot:
    container_name: gustelbot
    image: krippix/gustelbot
    volumes:
      - '/localPath/data/:/GustelBOT/data/'
    restart: unless-stopped
```
