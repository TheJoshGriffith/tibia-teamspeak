from urllib.request import urlopen
import urllib.error
import time, threading
from bs4 import BeautifulSoup
import DatabaseConnector

class TibiaCrawler(threading.Thread):

    def __init__(self, server_name, delay_seconds=60):
        threading.Thread.__init__(self)
        self.tibiaServer = "https://secure.tibia.com/community/?subtopic=worlds&world=" + server_name
        self.delaySeconds = delay_seconds
        self.dbc = DatabaseConnector.DatabaseConnector()

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

    def get_online_characters(self):
        online_character_list = []
        soup = BeautifulSoup(self.get_online_list_html(), 'html.parser')
        online_characters = soup.find_all("tr", {'class':'Odd'})
        online_characters += soup.find_all("tr", {'class':'Even'})
        for online_character in online_characters:
            soup = BeautifulSoup(str(online_character), 'html.parser')
            name = soup.find('td', {'style': 'width:70%;text-align:left;'}).get_text()
            level = soup.find('td', {'style': 'width:10%;'}).get_text()
            vocation = self.shorten_vocation(soup.find('td', {'style': 'width:20%;'}).get_text())
            online_character_list.append({'name': name.replace(u'\xa0', u' '), 'level': level, 'vocation': vocation})
        return online_character_list

    def character_still_online(self, name, online_characters):
        for online_character in online_characters:
            if online_character["name"] == name:
                return True
        return False

    def update_online_characters(self):
        online_characters = self.get_online_characters()
        for online_character in online_characters:
            if self.dbc.user_exists_by_name(online_character['name']):
                if not self.dbc.character_online(online_character['name']):
                    self.dbc.update_user_online_by_name(online_character['name'], online_character['level'])
            else:
                self.dbc.add_entry(online_character['name'], online_character['level'], online_character['vocation'], True)

        for db_online_character in self.dbc.get_online_characters():
            if self.character_still_online(db_online_character[1], online_characters):
                None
            else:
                self.dbc.update_user_offline_by_name(db_online_character[1])

    def get_online_list_html(self):
        responseContent = ""
        try:
            response = urlopen(self.tibiaServer)
            responseData = response.read()
            responseContent = responseData.decode('utf-8')
        except urllib.error.HTTPError as e:
            print("HTTP Error: " + e.reason)
        finally:
            return responseContent

    def run(self):
        while True:
            self.update_online_characters()
            time.sleep(self.delaySeconds)