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

## Environment Variables

Required environment variables are marked with a *

variable              | description
--------------------- | :------------------------------------
`DISCORD_TOKEN`*      | Discord token for authenticating the bot
`DISCORD_DEBUG_GUILDS`| comma separated list of guild id's to be set for debugging
`GUSTELBOT_LOGLEVEL`  | debug, info, warning, error, critical
`POSTGRES_HOST`*      | hostname of the postgresql server
`POSTGRES_PORT`       | defaults to 5432
`POSTGRES_DB`         | defaults to gustelbot
`POSTGRES_USER`*      | user with access to DB
`POSTGRES_PASSWORD`*  | password for user

## docker-compose example

```yaml
# https://github.com/krippix/GustelBOT
services:
  gustelbot:
    container_name: gustelbot
    image: krippix/gustelbot
    volumes:
      - './data/:/GustelBOT/data/'
    env_file: gustelbot.env
    restart: unless-stopped
```
