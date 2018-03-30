import threading, datetime, time, DatabaseConnector, logging


class TeamSpeakChannelUpdater(threading.Thread):
    def __init__(self, connector):
        threading.Thread.__init__(self)
        self.connector = connector
        self.dbc = DatabaseConnector.DatabaseConnector()
        self.log = logging.getLogger("TeamSpeakChannelUpdater")
        self.log.setLevel(logging.DEBUG)
        self.log_handler = logging.FileHandler("TeamSpeakChannelUpdater.log")
        self.log_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        self.log_handler.setFormatter(self.log_formatter)
        self.log.addHandler(self.log_handler)

    def update_list(self, list, cid):
        new_desc = ""
        count = 0
        for online_character in self.dbc.get_online_characters():
            if self.dbc.character_in_list(online_character[1].replace(u'\xa0', u' '), list):
                time_since = datetime.datetime.now() - datetime.datetime.strptime(online_character[5], "%Y-%m-%d %H:%M:%S.%f")
                minutes = int(time_since.seconds/60)
                hours = int(minutes/60)
                minutes = int(minutes%60)
                if self.dbc.is_list_notifications(list):
                    if not self.dbc.is_user_notified(online_character[1].replace(u'\xa0', u' ')):
                        self.connector.masspoke(online_character[1].replace(u'\xa0', u' ') + " logged in.")
                        err = self.dbc.set_user_notified(online_character[1].replace(u'\xa0', u' '))
                        if err:
                            print(err)
                time_since_string = '{:02}'.format(hours) + ":" + '{:02}'.format(minutes)
                new_desc += '[size=7][b][' + time_since_string + '][/b][/size] ' + '[img]https://tibiapf.com/' + online_character[3] + '.png[/img]  '  + str(online_character[2]) + ' ' + online_character[1] + ' ' + '\n'
                count += 1
        self.log.debug("Added %s characters to %s" % (count, list))
        header = "[b]" + list.title() + "List[/b] - " + str(count) + " out of " + str(self.dbc.count_list_memberships(list)) + " online\n[i]List name: !" + list + "[/i]\n\n"
        footer = "[i]" + "Last updated: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M %Z") + "[/i]"
        desc_to_set = header + new_desc + footer
        title_to_set = list.title() + " [" + str(count) + "]"
        self.connector.set_channel_description(int(cid), desc_to_set)
        if title_to_set != self.connector.get_channel_name(cid):
            self.connector.set_channel_name(int(cid), title_to_set)

    def update_respawn_system(self):
        if self.dbc.setting_exists("respawnlist"):
            header = "[b]Respawn List[/b] - [i]Put #code in your name to claim a respawn.[/i]\n\n"
            respawn_list_channel = self.dbc.get_setting("respawnlist")[0][2]
            desc_to_set = header
            for spawn in self.dbc.get_respawn_list():
                desc_to_set += spawn[2] + " - " + spawn[1] + " - " + spawn[3] + "\n"
            self.connector.set_channel_description(respawn_list_channel, desc_to_set)
        if self.dbc.setting_exists("respawnclaim"):
            header = "[b]Claimed Respawns[/b] - [i]Put #code in your name to claim a respawn. Note: It may take 5 seconds for the list to update.[/i]\n\n"
            respawn_claim_channel = self.dbc.get_setting("respawnclaim")[0][2]
            desc_to_set = header
            for spawn in self.dbc.get_claims():
                time_since = datetime.datetime.now() - datetime.datetime.strptime(spawn[5], "%Y-%m-%d %H:%M:%S.%f")
                minutes = int(time_since.seconds/60)
                hours = int(minutes/60)
                minutes = int(minutes%60)
                time_since_string = '{:02}'.format(hours) + ":" + '{:02}'.format(minutes)
                try:
                    desc_to_set += '[size=7][b][' + time_since_string + "][/b][/size] - " + spawn[2] + " - " + spawn[3] + " - " + str(spawn[4]) + "\n"
                except ts3.TS3Error as e:
                    print("Error appending respawn to claim system with respawn %s and error %s" % (spawn[2], e,))
            self.connector.set_channel_description(respawn_claim_channel, desc_to_set)

    def run(self):
        while(True):
            self.connector.update_claims()
            respawn_claim_channel = self.dbc.get_setting("respawnclaim")[0][2]
            self.connector.set_channel_description(respawn_claim_channel, "Now")
            time.sleep(3)
            for list in self.dbc.get_lists():
                self.update_list(list[1], list[2])
            self.update_respawn_system()
            time.sleep(5)
