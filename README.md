# GustelBot

This is my private Discord Bot I use for playing around.

## Administration

The Bot can be configured by using the `/config` command.

## Commands

command         | description
--------------- | :-------------
`/play <sound>` | Plays a specified sound, leave empty to pick randomly
`/folder`       | Plays random sound from specified folder
`/join`         | Bot joins your current channel
`/stop`         | Stops playback of current file
`/soundlist`    | Lists available sound files
`/ping`         | Replies with current ping
`/config`       | Various configuration options for the bot
  
## docker-compose example

```yaml
# https://github.com/krippix/GustelBOT
services:
  gustelbot:
    container_name: gustelbot
    image: krippix/gustelbot
    volumes:
      - './data/:/GustelBOT/data/'
    restart: unless-stopped
```
