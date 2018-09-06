import ts3
import threading
import logging
import DatabaseConnector
import os
from configparser import ConfigParser


class TeamSpeakReceiver(threading.Thread):

    def __init__(self, nickname, connector):
        threading.Thread.__init__(self)
        self.dbc = DatabaseConnector.DatabaseConnector()
        self.connector = connector
        self.log = logging.getLogger("TeamSpeakReceiver")
        self.log.setLevel(logging.DEBUG)
        self.log_handler = logging.FileHandler("TeamSpeakReceiver.log")
        self.log_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        self.log_handler.setFormatter(self.log_formatter)
        self.log.addHandler(self.log_handler)
        config = ConfigParser()
        config.read('config.ini')
        self.ts3conn = ts3.query.TS3Connection(config.get('serverinfo', 'TEAMSPEAK_IP'), config.get('serverinfo', 'TEAMSPEAK_PORT'))
        self.ts3conn.login(client_login_name=config.get('serverinfo', 'TEAMSPEAK_CLIENT_RECV'), client_login_password=config.get('serverinfo', 'TEAMSPEAK_PASSWD_RECV'))
        self.ts3conn.use(sid=str(config.get('serverinfo', 'TEAMSPEAK_SID')))
        self.ts3conn.send("clientupdate client_nickname=" + nickname)
        self.ts3conn.servernotifyregister(event="server")
        self.ts3conn.servernotifyregister(event="textprivate")

    def run(self):
        while True:
            self.ts3conn.send_keepalive()
            try:
                event = self.ts3conn.wait_for_event(timeout=150)
                self.log.debug("Event received")
            except ts3.query.TS3Error as e:
                self.log.debug(e)
                pass
            else:
                if "reasonid" in event[0]:
                    if event[0]["reasonid"] == '0':
                        if event[0]["client_type"] == '0':
                            self.log.debug("Client connected")
                            self.message_client(event[0]["clid"], "Welcome to TeamSpeak, use this channel to send commands!")
                        else:
                            self.log.debug("Not sending message to client because client_type is " + str(event[0]["client_type"]))
                elif "targetmode" in event[0]:
                    if event[0]["invokerid"] != self.ts3conn.whoami()[0]["client_id"]:
                        command, space, message = event[0]["msg"].partition(' ')
                        self.handle_message(command, message, event[0]["invokeruid"], event[0]["invokername"])

    def message_client(self, clid, message):
        res = self.ts3conn.sendtextmessage(targetmode=1, target=clid, msg=message)
        self.log.debug(res)

    def user_privileged(self, uid, permission):
        server_groups = self.connector.get_server_groups_uid(uid)
        if self.dbc.is_admin(uid) or self.dbc.server_groups_privileged(server_groups, permission):
            self.log.debug("Privileged servergroup: " + str(server_groups))
            return True
        else:
            self.log.debug("Non-privileged servergroup: " + str(server_groups))
            return False

    def handle_message(self, command, message, invokeruid, sender=None):
        self.log.debug(command)
        if command == "!help":
            self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Commands available:\n!masspoke\n!sg\n!addlist\n!removelist\n!channellist\n!alert\n!respawnlistchannel\n!claimedrespawnchannel")
        elif command == "!masspoke":
            if self.user_privileged(invokeruid, 'POKE'):
                self.connector.masspoke(message, invokeruid)
        elif command == "!addspawn":
            if message == "":
                self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid),"!addspawn [city],[code],[name]")
            else:
                city, code, spawn = message.split(',')
                err = self.dbc.add_respawn(city.lstrip().rstrip(), code.lstrip().rstrip().upper(), spawn.lstrip().rstrip())
                if err:
                    self.log.error("Error adding spawn: " + str(err))
                else:
                    self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Added spawn")
        elif command == "!exclude":
            if self.user_privileged(invokeruid, 'MAXI'):
                err = self.dbc.set_or_insert_setting("excluded_server_group", message)
                if err:
                    self.log.error("Error excluding server group: " + str(err))
                else:
                    self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Excluded server group successfully.")
        elif command == "!removespawn":
            # TODO: Implement remove spawn command
            self.log.fatal("Not yet implemented")
            self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Not yet implemented!")
            print("Not yet implemented")
        elif command == "!admin":
            if self.dbc.count_admins() == 0:
                self.dbc.add_admin(invokeruid)
                self.log.debug("Given admin permissions to " + str(invokeruid))
        elif command == "!sg":
            group, level = message.split(',')
            self.dbc.insert_privileged_server_group(group, level)
            self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Added server group to permissions table")
            self.log.debug("Added " + str(group) + " server group to privilege table with level " + str(level))
            self.log.debug("Add server group to privilege table")
        elif command == "!addlist":
            if self.user_privileged(invokeruid, 'LIST'):
                if message == "":
                    self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Use \"!addlist [name] [channelid]\" to add a list. You can view channels with !channellist. List name should contain 1 word without spaces.")
                else:
                    name, space, channel_id = message.partition(' ')
                    err = self.dbc.add_list(name.lower(), channel_id)
                    if err:
                        self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Failed to add list: " + str(err))
                    else:
                        self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "List added.")
            self.log.debug("Add a list to the character tracker")
        elif command == "!removelist":
            if self.user_privileged(invokeruid, 'LIST'):
                if message == "":
                    self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Use \"!remove [name]\" to remove a list.")
                else:
                    name, space, channel_id = message.partition(' ')
                    for character in self.dbc.get_list_characters(name):
                        err = self.dbc.remove_character_from_list(character, name)
                        if err:
                            self.log.error("Error removing character from list: " + str(err))
                    err = self.dbc.remove_list(name.lower())
                    if err:
                        self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Failed to add list: " + str(err))
                    else:
                        self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "List added.")
            self.log.debug("Remove a list from the character tracker")
        elif command == "!channellist":
            if self.user_privileged(invokeruid, 'LIST'):
                channel_message = ""
                for channel in self.connector.get_channel_list_string():
                    channel_message += channel + ", "
                    if len(channel_message) >= 950:
                        self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Channels: " + channel_message)
                        channel_message = ""
                self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Channels: " + channel_message)
            else:
                self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Insufficient permissions to list channels")
            self.log.debug("Send client a list of channels")
        elif command == "!alert":
            if self.user_privileged(invokeruid, 'LIST'):
                if message == "":
                    self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Use \"!alert [list] [on/off]\" to enable or disable poke notifications for a list.")
                else:
                    list, space, state = message.partition(' ')
                    err = self.dbc.set_list_notifications(list, True if state == 'on' else False)
                    if err:
                        self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Failed to set alerts:  " + str(err))
                    else:
                        self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Set alerts for channel successfully.")
            self.log.debug("Enable alerts for a given channel")
        elif command == "!setting":
            if self.user_privileged(invokeruid, 'MAXI'):
                if message == "":
                    self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Use \"!setting [settingname] [newvalue]\" to set a configuration setting.")
                else:
                    setting, space, value = message.partition(' ')
                    err = self.dbc.set_or_insert_setting(setting, value)
                    if err:
                        self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Failed to set setting:  " + str(err))
                    else:
                        self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Set setting successfully.")
        elif command == "!respawnlistchannel":
            if self.user_privileged(invokeruid, 'SPAWN'):
                if message == "":
                    self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Use \"!respawnlist [channel_id]\" to set a channel for the respawn list.")
                else:
                    err = self.dbc.set_or_insert_setting("respawnlist", message)
                    if err:
                        self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Failed to set respawnlist:  " + str(err))
                    else:
                        self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Set setting successfully.")
        elif command == "!claimedrespawnchannel":
            if self.user_privileged(invokeruid, 'SPAWN'):
                if message == "":
                    self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Use \"!respawnclaim [channel_id]\" to set a channel for the claimed respawn list.")
                else:
                    err = self.dbc.set_or_insert_setting("respawnclaim", message)
                    if err:
                        self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Failed to set respawnclaim:  " + str(err))
                    else:
                        self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Set setting successfully.")
        else:
            for list in self.dbc.get_lists():
                if command.lower() == "!" + list[1]:
                    if self.user_privileged(invokeruid, 'LIST'):
                        method, space, character = message.partition(' ')
                        if method == "add":
                            self.dbc.add_character_to_list(character, list[1])
                            self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Added user to list")
                        elif method == "remove":
                            self.dbc.remove_character_from_list(character, list[1])
                            self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Removed user from list")
                        elif method == "guild":
                            self.dbc.set_list_guild(list[1], character)
                            self.connector.message_client(self.connector.get_user_id_from_unique_id(invokeruid), "Set guild list")
