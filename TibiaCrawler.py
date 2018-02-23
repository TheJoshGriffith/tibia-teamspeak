from urllib.request import urlopen
import urllib.error
import time, threading
from bs4 import BeautifulSoup
import DatabaseConnector
import requests
import json

class TibiaCrawler(threading.Thread):

    def __init__(self, server_name, delay_seconds=10):
        threading.Thread.__init__(self)
        self.tibiaServer = "https://secure.tibia.com/community/?subtopic=worlds&world=" + server_name
        self.delaySeconds = delay_seconds
        self.dbc = DatabaseConnector.DatabaseConnector()
        self.world = "Olympa"

    def shorten_vocation(self, long):
        return {
            'Royal\xa0Paladin': 'RP',
            'Elite\xa0Knight': 'EK',
            'Master\xa0Sorcerer': 'MS',
            'Elder\xa0Druid': 'ED',
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
                    self.dbc.update_user_online_by_name(character["name"], character["level"])
                else:
                    self.dbc.add_entry(character["name"], character["level"], character["vocation"], True)

        for db_online_character in self.dbc.get_online_characters():
            if self.character_still_online_tibiadata(db_online_character[1], online_list):
                None
            else:
                self.dbc.update_user_offline_by_name(db_online_character[1])

    def run(self):
        while True:
            self.update_online_characters_tibiadata()
            time.sleep(self.delaySeconds)