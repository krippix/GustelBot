# GustelBot

My custom Discord Bot for experimenting.

## Ideas/TODO

- Make the soundlist embed interactive.
- ~~Try parsing said words in voice channels.~~ (Not Possible)

## Administration (currently not in use)

The admin commands of the bot can be used if the user fulfills one (or more) of the following conditions:

- role called "bot-admin"
- server administrator
- "manage channels" permission
- different voice files per server but try to prevent duplicates
- dynamic module loading

## Commands

command     | description
----------- | :-------------
disconnect  | Bot leaves its channel
play \<name> | Searches for soundfile and plays it in user's channel. (Random file if no selection is made)
stop        | Stops playback of current file
soundlist   | Lists available sound files
ping        | Replies with current ping
  
## Docker Installation
  
### Build

```sh
docker build . -t krippix/gustelbot
```
  
### docker-compose example

```yaml
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
