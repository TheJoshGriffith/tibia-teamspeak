import sqlite3
import datetime
import pprint

class DatabaseConnector():

    def __init__(self):
        self.db = sqlite3.connect('tibiats3.db')
        self.setup_db()

    def sql_edit(self, sql, kwargs=None):
        db = sqlite3.connect('tibiats3.db')
        cursor = db.cursor()
        try:
            if kwargs == None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, kwargs)
            db.commit()
        except sqlite3.Error as e:
            return e
        finally:
            db.close()
        if cursor.rowcount == 0:
            return "No rows affected"
        return False

    def sql_count(self, sql, kwargs=None):
        db = sqlite3.connect('tibiats3.db')
        cursor = db.cursor()
        try:
            if kwargs == None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, kwargs)
            return len(cursor.fetchall())
        except sqlite3.Error as e:
            db.close()
            return e
        finally:
            db.close()

    def sql_get(self, sql, kwargs=None):
        db = sqlite3.connect('tibiats3.db')
        try:
            cursor = db.cursor()
            if kwargs == None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, kwargs)
            return cursor.fetchall()
        except sqlite3.Error as e:
            db.close()
            return e
        finally:
            db.close()

    def table_exists(self, name):
        db = sqlite3.connect('tibiats3.db')
        cursor = db.cursor()
        cursor.execute('''SELECT name FROM sqlite_master WHERE name=?''', (name,))
        count = len(cursor.fetchall())
        if count == 1:
            return True
        else:
            return False

    def setup_db(self):
        if not self.table_exists('characters'):
            self.sql_edit('''CREATE TABLE characters(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, level INT, vocation TEXT, online BOOLEAN, updated TIMESTAMP)''')
        if not self.table_exists('admins'):
            self.sql_edit('''CREATE TABLE admins(id INTEGER PRIMARY KEY AUTOINCREMENT, identity TEXT UNIQUE)''')
        if not self.table_exists('privileged_server_groups'):
            self.sql_edit('''CREATE TABLE privileged_server_groups(id INTEGER PRIMARY KEY AUTOINCREMENT, server_group TEXT UNIQUE)''')
        if not self.table_exists('lists'):
            self.sql_edit('''CREATE TABLE lists(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, channel_id INT UNIQUE, notifications BOOLEAN DEFAULT FALSE)''')
        if not self.table_exists('list_memberships'):
            self.sql_edit('''CREATE TABLE list_memberships(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, list TEXT, notified BOOLEAN)''')
        if not self.table_exists('spawns'):
            self.sql_edit('''CREATE TABLE spawns(id INTEGER PRIMARY KEY AUTOINCREMENT, city TEXT, code TEXT UNIQUE, name TEXT, claimer TEXT, updated TIMESTAMP)''')
            self.fill_respawn_list()
        if not self.table_exists('settings'):
            self.sql_edit('''CREATE TABLE settings(id INTEGER PRIMARY KEY AUTOINCREMENT, setting TEXT UNIQUE, val TEXT)''')

    def get_respawn_list(self):
        return self.sql_get('''SELECT * FROM spawns ORDER BY city ASC''')

    def set_or_insert_setting(self, setting, val):
        if self.sql_count('''SELECT * FROM settings WHERE setting=?''', (setting,)):
            return self.sql_edit('''UPDATE settings SET val=? WHERE setting=?''', (val, setting,))
        else:
            return self.sql_edit('''INSERT INTO settings(setting, val) values(?,?)''', (setting,val,))

    def add_respawn(self, city, code, spawn):
        return self.sql_edit('''INSERT INTO spawns(city, code, name) values(?,?,?)''', (city,code,spawn,))

    def get_setting(self, setting):
        return self.sql_get('''SELECT * FROM settings WHERE setting=?''', (setting,))

    def setting_exists(self, setting):
        return self.sql_count('''SELECT * FROM settings WHERE setting=?''', (setting,))

    def fill_respawn_list(self):
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Darashia', 'D1', 'Drefia Grim Reapers (Floor 1)')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Darashia', 'D2', 'Drefia Grim Reapers (Floor 1 & 2)')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Darashia', 'D3', 'Drefia Grim Reapers (Floor 2)')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Darashia', 'D4', 'Drefia Grim Reapers (Floor 2 & 3)')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Darashia', 'D5', 'Drefia Grim Reapers (Floor 3)')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Darashia', 'D6', 'Drefia Grim Reapers (Floor 1 & 2 & 3)')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Edron', 'E1', 'EK Soils')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Edron', 'E2', 'ED Soils')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Edron', 'E3', 'MS Soils')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Edron', 'E4', 'RP Soils')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Edron', 'E9', 'Demon new')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Edron', 'E13', 'New Heros')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Edron', 'E14', 'Wereboars land')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Farmine', 'H1', 'Lizard City')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Farmine', 'H2', 'Souleaters')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Farmine', 'H4', 'Brimstone Bugs Surface')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Farmine', 'H6', 'Corruption Hole -2')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Farmine', 'H7', 'Corruption Hole -1')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Farmine', 'H8', 'New Chosens')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Farmine', 'H10', 'Ghastly Dragons')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Farmine', 'H11', 'Ghastly Dragons Palace')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Farmine', 'H12', 'Draken Abominations')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Farmine', 'H13', 'Drakens Abominations & Undead Dragons')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Farmine', 'H14', 'Draken Walls')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Farmine', 'H26', 'Yielothax')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Ferumbras Ascension', 'Z1', 'Razzargon Seal')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Ferumbras Ascension', 'Z2', 'Ragiaz Seal')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Ferumbras Ascension', 'Z3', 'Zamulosh Seal')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Ferumbras Ascension', 'Z4', 'Mazoran Seal')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Ferumbras Ascension', 'ZS', 'Tarbaz Seal')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Ferumbras Ascension', 'Z6', 'Shulgrax Seal')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Ferumbras Ascension', 'Z7', 'Plagirath Seal')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Ferumbras Ascension', 'Z8', 'Entrance Whole Floor')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Ferumbras Ascension', 'Z9', 'Between Seals')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Ferumbras Ascension', 'Z10', 'Ferumbras Road')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Goroma', 'I2', 'Goroma SerpentsS. East East')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Goroma', 'I3', 'Goroma SerpentsS. West West')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Goroma', 'I4', 'Goroma SS MainFloor')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Goroma', 'I7', 'Ferumbras Tower')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Goroma', 'I8', 'Giant Spider Isle')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Goroma', 'I11', 'Ouara Scout (GS Island)')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Goroma', 'I16', 'Goroma Demons')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Inquisition', 'Fl', 'Hellfire Fighter and Spectres')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Inquisition', 'F2', 'Hellfire fighters, Spectres and Quaras')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Inquisition', 'F3', 'Dark Torturer Seal')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Inquisition', 'F4', 'The Vats Inquisition')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Inquisition', 'F5', 'Battlefield')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Inquisition Bosses', 'G1', 'Ushuriel')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Inquisition Bosses', 'G2', 'Zugurosh')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Inquisition Bosses', 'G3', 'Madareth')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Inquisition Bosses', 'G4', 'Annihilion')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Inquisition Bosses', 'G5', 'Hellgorak')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Kazordoon', 'K6', 'Spikes Tasks UP')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Kazordoon', 'K7', 'Spikes Tasks Down')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Kazordoon', 'K8', 'Lower Spike (Last Floor)')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Oramond', 'M1', 'Hydras & Bog Riders Oramond')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Oramond', 'M2', 'East Minos Oramond')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Oramond', 'M3', 'North East Minos Oramond')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Oramond', 'M4', 'North Minos Oramond')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Oramond', 'M5', 'West Oramond (Ouaras)')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Oramond', 'M11', 'Glooth B. West')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Oramond', 'M12', 'Glooth B. East')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Oramond', 'M13', 'Glooth B. South')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Oramond', 'M17', 'Whole Catacombs')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Oramond', 'M18', 'Raids')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Oramond', 'M19', 'Seacrest Grounds')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Oramond', 'M20', 'Fury / spectres Oramond')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Pits of Inferno', 'Y1', 'Apocalypse Seal')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Pits of Inferno', 'Y2', 'Ashfalor')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Pits of Inferno', 'Y3', 'Bazir Seal')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Pits of Inferno', 'Y4', 'Infernatil Seal')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Pits of Inferno', 'Y5', 'Pumin Seal')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Pits of Inferno', 'Y6', 'Tafariel Seal')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Pits of Inferno', 'Y7', 'Verminor Seal')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Port Hope', 'N2', 'Banuta -1')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Port Hope', 'N3', 'Banuta -2')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Port Hope', 'N4', 'Banuta -1 & -2')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Port Hope', 'N5', 'Banuta -3')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Port Hope', 'N6', 'Banuta -3 & -4')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Port Hope', 'N7', 'Banuta -4')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Port Hope', 'N8', 'Forbidden Land Hydras')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Port Hope', 'N9', 'Forbidden Land Behemoth')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Port Hope', 'N10', 'Forbidden Land Giant Spiders')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Port Hope', 'N18', 'Medusa Tower')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Port Hope', 'N19', 'New Giants Spider')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Port Hope', 'N20', 'Orientals Spawn(Azuras)')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Roshamuul', 'O1', 'Roshamuul before bridge (West)')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Roshamuul', 'O2', 'Roshamuul before bridge (East)')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Roshamuul', 'O3', 'Roshamuul Bridge')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Roshamuul', 'O4', 'Guzzlemaw Valley (West)')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Roshamuul', 'O5', 'Guzzlemaw Valley (East)')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Roshamuul', 'O6', 'Roshamuul Prison -1')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Roshamuul', 'O7', 'Roshamuul Prison -2')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Roshamuul', 'O8', 'Roshamuul Prison -3')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Roshamuul', 'O9', 'Nightmare Isles')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Roshamuul', 'O10', 'Whole Guzzlemaw Valley')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Roshamuul', 'O11', 'Roshamuul Dego- Retchings')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Vortex', 'X1', 'Darama')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Vortex', 'X2', 'Svargrond')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Vortex', 'X3', 'ZAO')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Vortex', 'X4', 'Edron')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Vortex', 'X5', 'Kazordoon')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Yalahar', 'S1', 'Yalahar Demons West')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Yalahar', 'S2', 'Yalahar Demons East')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Yalahar', 'S3', 'Fenrock Dragon Lords')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Yalahar', 'S4', 'Grim Reapers Yalahar West')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Yalahar', 'S5', 'Grim Reapers Yalahar East')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Yalahar', 'S6', 'Sunken Ouaras')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Yalahar', 'S7', 'Vengoth Castle')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Yalahar', 'S19', 'Giant Spider Yalahar')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Yalahar', 'S21', 'Hellspawn Ground Floor')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Yalahar', 'S22', 'Hellspawns -1')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Yalahar', 'S28', 'Nightmares Yalahar')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Yalahar', 'S37', 'War Golems (Old Spawns)')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Yalahar', 'S38', 'War Golems (New West)')''')
        self.sql_edit('''INSERT INTO spawns(city, code, name) values('Yalahar', 'S39', 'War Golems (New East)')''')

    def get_claims(self):
        return self.sql_get('''SELECT * FROM spawns WHERE claimer NOT NULL''')

    def is_claimed(self, respawn):
        return self.sql_count('''SELECT * FROM spawns WHERE claimer NOT NULL and code=?''', (respawn.upper(),)) == 1

    def claim_respawn(self, respawn, claimer):
        return self.sql_edit('''UPDATE spawns SET claimer=?,updated=? WHERE code=?''', (claimer,datetime.datetime.now(),respawn,))

    def unclaim_respawn(self, respawn):
        return self.sql_edit('''UPDATE spawns SET claimer=NULL,updated=NULL WHERE code=?''', (respawn,))

    def set_list_notifications(self, list, state):
        return self.sql_edit('''UPDATE lists SET notifications=? WHERE name=?''', (state, list,))

    def is_list_notifications(self, list_name):
        return self.sql_get('''SELECT * FROM lists WHERE name=?''', (list_name,))[0][3] == 1

    def get_lists(self):
        return self.sql_get('''SELECT * FROM lists''')

    def get_list_characters(self, list):
        return self.sql_get('''SELECT * FROM list_memberships WHERE list=?''', (list,))

    def add_character_to_list(self, name, list):
        return self.sql_edit('''INSERT INTO list_memberships(name, list) VALUES(?,?)''', (name,list,))

    def remove_character_from_list(self, name, list):
        return self.sql_edit('''DELETE FROM list_memberships WHERE name=? AND list=?''', (name, list,))

    def remove_list(self, listname):
        return self.sql_edit('''DELETE FROM lists WHERE name=?''', (listname,))

    def add_list(self, name, channel_id):
        return self.sql_edit('''INSERT INTO lists(name, channel_id) VALUES(?,?)''', (name, channel_id,))

    def server_groups_privileged(self, groups):
        for group in groups.split(','):
            if self.sql_count('''SELECT * FROM privileged_server_groups WHERE server_group=?''', (group,)) == 1:
                return True
        return False

    def is_admin(self, uid):
        return self.sql_count('''SELECT * FROM admins WHERE identity=?''', (uid,)) == 1

    def is_privileged_user(self, server_group):
        return self.sql_count('''SELECT * FROM privileged_server_groups WHERE servergroup=?''', (server_group,)) == 1

    def insert_privileged_server_group(self, group):
        return self.sql_edit('''INSERT INTO privileged_server_groups(server_group) VALUES(?)''', (group,))

    def count_admins(self):
        return self.sql_count('''SELECT * FROM admins''')

    def add_admin(self, identity):
        return self.sql_edit('''INSERT INTO admins(identity) VALUES(?)''', (identity,))

    def add_entry(self, name, level, vocation, online):
        return self.sql_edit('''INSERT INTO characters(name, level, vocation, online, updated) VALUES(?, ?, ?, ?, ?)''', (name, level, vocation, online, datetime.datetime.now()))

    def find_entry_by_name(self, name):
        character = self.sql_get('''SELECT * FROM characters WHERE name=?''', (name,))[0]
        return {'name': character[1], 'level': character[2], 'vocation': character[3], 'online': character[4], 'updated': character[5]}

    def update_user_offline_by_name(self, name):
        self.sql_edit('''UPDATE characters SET online=?, UPDATED=? WHERE name=?''', (False, datetime.datetime.now(), name,))

    def update_user_online_by_name(self, name, level):
        self.sql_edit('''UPDATE list_memberships SET notified=? where name=?''', (False,name,))
        return self.sql_edit('''UPDATE characters SET online=?, level=?, UPDATED=? WHERE name=?''', (True, level, datetime.datetime.now(), name,))

    def set_user_notified(self, name):
        return self.sql_edit('''UPDATE list_memberships SET notified=? WHERE name=?''', (True,name,))

    def is_user_notified(self, name):
        return self.sql_count('''SELECT * FROM list_memberships WHERE name=? AND notified=?''', (name,True,)) == 1

    def user_exists_by_name(self, name):
        if self.sql_count('''SELECT * FROM characters WHERE name=?''', (name,)) == 1:
            return True
        else:
            return False

    def get_online_characters(self):
        return self.sql_get('''SELECT * FROM characters WHERE online=1 ORDER BY vocation ASC, level DESC''')

    def character_online(self, character):
        if self.sql_count('''SELECT * FROM characters WHERE name=? AND online=1''', (character,)) == 1:
            return True
        else:
            return False

    def character_in_list(self, character, list):
        if self.sql_count('''SELECT * FROM list_memberships WHERE name=? AND list=?''', (character, list,)) == 1:
            return True
        else:
            return False

    def count_list_memberships(self, list):
        return self.sql_count('''SELECT * FROM list_memberships WHERE list=?''', (list,))