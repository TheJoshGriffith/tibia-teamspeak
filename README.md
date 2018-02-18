# Tibia Teamspeak Bot

### About
This is a bot for TeamSpeak which provides information to a TeamSpeak server about online
characters, as well as offering a respawn claiming system to users and a few other handy features.

### Installation
You'll need a few pre-requesites to make this work, namely:
* ts3
* configparser
* bs4
* requests
* jinja2
* cherrypy

Once these are installed, simply copy `config.ini.sample` to `config.ini`, and enter your server
credentials. You will need to create 2 ServerQuery login accounts, preferably using separate
identities. You can do this within TeamSpeak, as long as you have the permissions, by hitting
Tools, then ServerQuery Login. Enter a username and take note of the details provided.

### Usage
Running the bot is as simple as running `main.py`. This will initialise everything, create the
database file if it doesn't exist already. From there, join your TeamSpeak server, and you will 
receive a message from a user called TibiaTS3 - send this user a message back saying `!admin` and
that user will add you to the privilege table. This only works for the first user.

After this, you can add privileged users by sending a message with `!sg <ServerGroupID>` - the 
ServerGroupID parameter can be found in the TeamSpeak Server Groups dialog, just use the number.

Send the bot a command `!help` for a full list of commands. You'll need to use `!channellist` to 
get a list of channels with their IDs to use to create lists and respawn claiming systems, which
can then be configured using its other commands.
