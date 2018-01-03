import ts3
import queue
import threading
import logging
import time
import datetime
import os
from configparser import ConfigParser



class TeamSpeakSender(threading.Thread):

    def __init__(self, nickname):
        threading.Thread.__init__(self)
        self.log = logging.getLogger("TeamSpeakSender")
        self.log.setLevel(logging.DEBUG)
        self.log_handler = logging.FileHandler("TeamSpeakSender.log")
        self.log_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        self.log_handler.setFormatter(self.log_formatter)
        self.log.addHandler(self.log_handler)
        config = ConfigParser()
        config.read('config.ini')
        self.ts3conn = ts3.query.TS3Connection(config.get('serverinfo', 'TEAMSPEAK_IP'), config.get('serverinfo', 'TEAMSPEAK_PORT'))
        self.ts3conn.login(client_login_name=config.get('serverinfo', 'TEAMSPEAK_CLIENT_SEND'), client_login_password=config.get('serverinfo', 'TEAMSPEAK_PASSWD_SEND'))
        self.ts3conn.use(sid=str(config.get('serverinfo', 'TEAMSPEAK_SID')))
        self.ts3conn.send("clientupdate client_nickname=" + nickname)
        self.q = queue.Queue()
        self.q_output = queue.Queue()
        self.events_per_second = 25

    def run(self):
        while True:
            try:
                queue_item = self.q.get(timeout=150)
                self.q_output.put(queue_item())
                self.q.task_done()
                time.sleep(1/self.events_per_second)
            except queue.Empty:
                self.ts3conn.send_keepalive()
            except:
                self.log.error("Error processing queue item")
                print("Error processing queue item at: " + str(datetime.datetime.now()))