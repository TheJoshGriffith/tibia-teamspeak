import TeamSpeakReceiver, TeamSpeakSender, TeamSpeakChannelUpdater, DatabaseConnector, logging, re


class TeamSpeakConnector:

    def __init__(self):
        self.dbc = DatabaseConnector.DatabaseConnector()
        self.tss = TeamSpeakSender.TeamSpeakSender("Updater")
        self.tss.start()
        self.tsr = TeamSpeakReceiver.TeamSpeakReceiver("TibiaTS3", self)
        self.tsr.start()
        self.tscu = TeamSpeakChannelUpdater.TeamSpeakChannelUpdater(self)
        self.tscu.start()
        self.log = logging.getLogger("TeamSpeakConnector")
        self.log.setLevel(logging.DEBUG)
        self.log_handler = logging.FileHandler("TeamSpeakConnector.log")
        self.log_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        self.log_handler.setFormatter(self.log_formatter)
        self.log.addHandler(self.log_handler)

    def get_server_groups(self, client_database_id):
        self.tss.q.put(lambda: self.tss.ts3conn.servergroupsbyclientid(cldbid=client_database_id))
        res = self.tss.q_output.get()
        return res[0]['sgid']

    def get_server_groups_uid(self, client_uid):
        self.tss.q.put(lambda: self.tss.ts3conn.clientgetids(cluid=client_uid))
        client_id = self.tss.q_output.get()
        self.tss.q.put(lambda: self.tss.ts3conn.clientinfo(clid=client_id[0]["clid"]))
        client_info = self.tss.q_output.get()
        return client_info[0]["client_servergroups"]

    def masspoke(self, message, sender=None):
        self.log.debug("Masspoke with InvokerUID: " + str(sender) + ", with message: " + message)
        self.tss.q.put(lambda: self.tss.ts3conn.clientlist())
        clients = self.tss.q_output.get()
        for client in clients:
            if client['client_type'] == '0':
                if self.dbc.setting_exists("excluded_server_group"):
                    for server_group in self.get_server_groups(client['client_database_id']).split(','):
                        if server_group == self.dbc.get_setting("excluded_server_group")[0][2]:
                            break
                        self.log.debug("Poking client with name: " + client['client_nickname'] + ", CLID: " + client['clid'] + " and type: " + str(client['client_type']))
                        self.tss.q.put(lambda: self.tss.ts3conn.clientpoke(msg=message, clid=client['clid']))
                        res = self.tss.q_output.get()
                        self.log.debug("Masspoked with error: " + str(res))
                else:
                    self.log.debug("Poking client with name: " + client['client_nickname'] + ", CLID: " + client['clid'] + " and type: " + str(client['client_type']))
                    self.tss.q.put(lambda: self.tss.ts3conn.clientpoke(msg=message, clid=client['clid']))
                    res = self.tss.q_output.get()
                    self.log.debug("Masspoked with error: " + str(res))

    def message_client(self, client_id, message):
        self.log.debug("Message client: " + str(client_id) + " " + message)
        self.tss.q.put(lambda: self.tss.ts3conn.sendtextmessage(targetmode=1, target=client_id, msg=message))
        res = self.tss.q_output.get()
        self.log.debug(res)
        return res

    def get_user_id_from_unique_id(self, uid):
        self.log.debug("Getting user_id for " + str(uid))
        self.tss.q.put(lambda: self.tss.ts3conn.clientgetids(cluid=uid)[0]["clid"])
        res = self.tss.q_output.get()
        self.log.debug(res)
        return res

    def get_channel_list_string(self):
        channel_list = []
        self.tss.q.put(lambda: self.tss.ts3conn.channellist())
        res = self.tss.q_output.get()
        self.log.debug(res)
        for channel in res:
            channel_list.append(channel["channel_name"] + " - " + channel["cid"])
        return channel_list

    def get_channel_name(self, channel_id):
        self.tss.q.put(lambda: self.tss.ts3conn.channelinfo(cid=channel_id))
        res = self.tss.q_output.get()
        self.log.debug(res[0])
        return res[0]["channel_name"]

    def set_channel_name(self, channel_id, new_name):
        self.tss.q.put(lambda: self.tss.ts3conn.channeledit(cid=channel_id, channel_name=new_name))
        res = self.tss.q_output.get()
        self.log.debug(res)
        return res

    def set_channel_description(self, channel_id, new_description):
        self.tss.q.put(lambda: self.tss.ts3conn.channeledit(cid=channel_id, channel_description=new_description))
        res = self.tss.q_output.get()
        self.log.debug(res)
        return res

    def get_channel_description(self, channel_id):
        self.tss.q.put(lambda: self.tss.ts3conn.channelinfo(cid=channel_id))
        res = self.tss.q_output.get()
        self.log.debug("Description: " + res[0]['channel_description'])
        return res[0]['channel_description']

    def update_claims(self):
        self.tss.q.put(lambda: self.tss.ts3conn.clientlist())
        res = self.tss.q_output.get()
        for teamspeak_client in res:
            if teamspeak_client["client_type"] != "1":
                if re.search("#[a-zA-Z]{1,2}[0-9]{1,2}", teamspeak_client["client_nickname"]):
                    matches = re.findall("#[a-zA-Z]{1,2}[0-9]{1,2}", teamspeak_client["client_nickname"])
                    for match in matches:
                        if not self.dbc.is_claimed(str(match[1:])):
                            err = self.dbc.claim_respawn(str(match[1:]).upper(), teamspeak_client["client_nickname"])
                            if err:
                                self.log.error(err)
        claims = self.dbc.get_claims()
        if len(claims) != 0:
            for claimed_respawn in claims:
                if not self.client_exists_with_name(str(claimed_respawn[4])):
                    self.dbc.unclaim_respawn(claimed_respawn[2])

    def get_client_name(self, client_id):
        self.tss.q.put(lambda: self.tss.ts3conn.clientlist())
        res = self.tss.q_output.get()
        for teamspeak_client in res:
            if teamspeak_client["clid"] == client_id:
                return teamspeak_client["client_nickname"]
        return ""

    def client_exists_with_name(self, name):
        self.tss.q.put(lambda: self.tss.ts3conn.clientlist())
        res = self.tss.q_output.get()
        for teamspeak_client in res:
            if teamspeak_client["client_nickname"] == name:
                return teamspeak_client["client_nickname"]
        return ""

    def get_client_description(self, client_id):
        self.tss.q.put(lambda: self.tss.ts3conn.clientinfo(clid=client_id))
        res = self.tss.q_output.get()
        return res[0]["client_description"]