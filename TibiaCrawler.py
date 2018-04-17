import time, threading
import DatabaseConnector
import requests
import json
from configparser import ConfigParser

class TibiaCrawler(threading.Thread):

    def __init__(self, delay_seconds=10):
        threading.Thread.__init__(self)
        self.delaySeconds = delay_seconds
        self.dbc = DatabaseConnector.DatabaseConnector()
        config = ConfigParser()
        config.read('config.ini')
        self.world = config.get('settings', 'GAME_SERVER')
        self.tibiaServer = "https://secure.tibia.com/community/?subtopic=worlds&world=" + self.world

    def get_guild_members(self, guild):
        guild_url = "https://api.tibiadata.com/v2/guild/" + guild + ".json"
        res = requests.get(guild_url)
        while res.status_code != 200:
            res = requests.get(guild_url)
        content = json.loads(res.content.decode('utf-8'))
        ranks = content['guild']['members']
        member_list = []
        for rank in ranks:
            for member in rank['characters']:
                member_list.append(member['name'])
        return member_list

    def add_new_guild_members(self, list, guild):
        for member in self.get_guild_members(guild):
            if not self.dbc.character_in_list(member, list):
                self.dbc.add_character_to_list(member, list, True)

    def check_and_remove_existing_guild_members(self, list, guild):
        list_entries = self.get_guild_members(guild)
        for member in self.dbc.get_list_characters(list):
            if not member in list_entries:
                self.dbc.remove_character_from_list(member, list)

    def shorten_vocation(self, long):
        return {
            'Royal Paladin': 'RP',
            'Elite Knight': 'EK',
            'Master Sorcerer': 'MS',
            'Elder Druid': 'ED',
            'Paladin': 'RP',
            'Knight': 'EK',
            'Sorcerer': 'MS',
            'Druid': 'ED',
            'None': 'NA',
        }[long]

    def get_online_characters_tibiadata(self):
        server_url = "https://api.tibiadata.com/v2/world/" + self.world + ".json"
        res = requests.get(server_url)
        while res.status_code != 200:
            res = requests.get(server_url)
        servers = json.loads(res.content.decode('utf-8'))
        return servers

    def character_still_online_tibiadata(self, name, list):
        for character in list:
            if character["name"] == name:
                return True
        return False

    def update_online_characters_tibiadata(self):
        try:
            online_list = self.get_online_characters_tibiadata()["world"]["players_online"]
        except KeyError as e:
            online_list = []
            print("Key error getting online list, assuming server save: %s" % e)

        for character in online_list:
            if self.dbc.user_exists_by_name(character["name"]):
                if not self.dbc.character_online(character["name"]):
                    if not self.dbc.character_investigated(character["name"]):
                        self.dbc.add_entry(character["name"], character["level"], self.shorten_vocation(character["vocation"]), True)
                    else:
                        self.dbc.update_user_online_by_name(character["name"], character["level"])
                else:
                    self.dbc.add_entry(character["name"], character["level"], character["vocation"], True)

        for db_online_character in self.dbc.get_online_characters():
            if self.character_still_online_tibiadata(db_online_character[1], online_list):
                None
            else:
                self.dbc.update_user_offline_by_name(db_online_character[1])

        for db_list in self.dbc.get_list_guilds():
            self.add_new_guild_members(db_list[1], db_list[2])
            self.check_and_remove_existing_guild_members(db_list[1], db_list[2])

    def get_character(self, name):
        url = ''.join(["https://api.tibiadata.com/v2/character/", name, ".json"])
        res = requests.get(url)
        while res.status_code != 200:
            res = requests.get(url)
        return res.content.decode('utf-8')

    def run(self):
        while True:
            self.update_online_characters_tibiadata()
            time.sleep(self.delaySeconds)