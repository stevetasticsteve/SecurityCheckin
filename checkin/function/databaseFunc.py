import datetime
import logging
import sqlite3
import sys

from checkin.function.logSettings import create_logger, close_logging

logger = create_logger(__name__)
logger.addHandler(logging.StreamHandler())

version = 0.511
accepted_db_version = 0.4


class DatabaseConnect:
    def __init__(self):
        try:
            self.conn = sqlite3.connect('checkins.db',
                                        detect_types=sqlite3.PARSE_DECLTYPES |
                                                    sqlite3.PARSE_COLNAMES)
            self.c = self.conn.cursor()
            self.logger = create_logger(__name__)
            self.logger.debug('db connected')
            self.c.execute('''CREATE TABLE IF NOT EXISTS tribalLocations(
                            tribe TEXT PRIMARY KEY,
                            family TEXT,
                            information TEXT,
                            Active TEXT)''')

            self.c.execute('''CREATE TABLE IF NOT EXISTS checkInMethods(
                            method TEXT PRIMARY KEY)''')
            try:
                self.formsOfCommunication = [('Phone',), ('Email',),
                                             ('Inreach',), ('Radio',), ('Facebook',)]
                for comm in self.formsOfCommunication:
                    self.c.execute('''INSERT INTO checkInMethods(method)
                                   VALUES(?)''', comm)
                    self.conn.commit()
            except sqlite3.IntegrityError:
                pass

            self.c.execute('''CREATE TABLE IF NOT EXISTS checkIns
                            (tribe TEXT,
                            checkInMethod TEXT,
                            logged DATE PRIMARY KEY,
                            date DATE)''')

            self.c.execute('''CREATE TABLE IF NOT EXISTS meta
                            (version REAL,
                            area TEXT,
                            appID TEXT PRIMARY KEY)''')

            try:
                self.c.execute('''INSERT INTO meta(version, area, appID)
                               VALUES(?, ?, ?)''', (version, 'Central Area',
                                                    'CheckinApp2019'))
                self.conn.commit()
            except sqlite3.IntegrityError:
                pass
        except Exception:
            self.logger.exception('__init__ error')

    def handle_error(self):
        self.conn.rollback()
        self.logger.exception('Database error, rollback initiated.')
        self.conn.close()
        self.logger.debug('db successfully closed.')
        sys.exit()

    def add_tribal_location(self, name, family):
        try:
            self.c.execute('''INSERT INTO tribalLocations(tribe, family, information, active)
                            VALUES(?, ?, '' ,'True' )''', (name, family))
            self.conn.commit()
        except sqlite3.IntegrityError:
            raise sqlite3.IntegrityError
        except Exception:
            self.handle_error()

    def list_active_tribal_info(self):
        try:
            self.c.execute('''SELECT tribe, family FROM tribalLocations
                            WHERE Active = ('True') ''')
            data = self.c.fetchall()
            return data
            # returns a list of tuples (tribe, family units)
        except Exception:
            self.handle_error()

    def list_inactive_tribal_info(self):
        try:
            self.c.execute('''SELECT tribe, family FROM tribalLocations
                            WHERE Active = ('False') ''')
            data = self.c.fetchall()
            return data
            # returns a list of tuples (tribe, family units)
        except Exception:
            self.handle_error()

    def list_all_tribal_locations(self):
        # This function returns a list of both active and inactive works
        try:
            active = self.list_active_tribal_info()
            inactive = self.list_inactive_tribal_info()
            tribal_locations = []
            for tup in active:
                tribal_locations.append(tup)
            for tup in inactive:
                tribal_locations.append(tup)
            return tribal_locations
            # returns a list of tuples (tribe, family units) active + inactive
        except Exception:
            self.handle_error()

    def list_checkin_methods(self):
        try:
            self.c.execute('''SELECT method FROM checkInMethods ''')
            return self.c.fetchall()
        except Exception:
            self.handle_error()

    def log_check_in(self, tribe, method, date):
        try:
            self.c.execute('''SELECT date as "date [timestamp]"
                            FROM checkIns WHERE tribe = ?''', (tribe,))
            data = self.c.fetchall()
            temp = []
            for item in data:
                temp.append(item[0])

            if date in temp:
                return 'Already checked in'
            else:
                self.c.execute('''INSERT INTO checkIns (tribe, checkInMethod, date, logged)
                               VALUES (?, ?, ?, ?) ''',
                               (tribe, method, date, datetime.datetime.now()))
                self.conn.commit()
                self.logger.debug(tribe + ' logged as checked in via ' + method)
        except Exception:
            self.handle_error()

    def get_last_check_in(self, tribe):
        try:
            self.c.execute('''SELECT date as "date [timestamp]"
                            FROM checkIns WHERE tribe = ? ''', (tribe,))
            data = self.c.fetchall()
            if not data:
                return 'n/a'
            latest_check_in = max(data)
            return latest_check_in[0]
        except Exception:
            self.handle_error()

    def sort_tribes_by_last_checkin(self):
        # Used to get all active tribal locations sorted by date of last checkin,
        # used in the drawActiveWidget function
        try:
            activeTribes = self.c.execute('''SELECT tribe, family FROM
                                            tribalLocations
                                            WHERE Active = ('True') ''')
            data = self.c.fetchall()
            tribes = []
            # Use the tribe name to retrive it's last checkin datetime
            # and add it at index 0
            for tup in data:
                tup = list(tup)
                tup.insert(0, self.get_last_check_in(tup[0]))
                # If tribe not checked in ever 'n/a' will crash the sort
                if type(tup[0]) == str:
                    tup[0] = datetime.datetime.now()
                tribes.append(tup)
            # sort by datetime
            tribes.sort()
            # remove the datetime object
            for tup in tribes:
                tup.remove(tup[0])
            # return a list of lists (tribe, family)
            return tribes
        except Exception:
            self.handle_error()

    def sort_alphabetically(self):
        # Used to get all active tribal locations sorted alphabetically,
        # used in the drawActiveWidget function
        try:
            self.c.execute('''SELECT tribe, family FROM
                                tribalLocations
                                WHERE Active = ('True') ''')
            data = self.c.fetchall()
            tribes = []
            # convert into a list of lists
            for tup in data:
                tup = list(tup)
                tribes.append(tup)
            # sort alphabetically
            tribes.sort()
            # returns a list of lists
            return tribes
        except Exception:
            self.handle_error()

    def get_last_checkin_method(self, tribe):
        try:
            date = self.get_last_check_in(tribe)
            self.c.execute('''SELECT method FROM checkInMethods''')
            checkinMethods = self.c.fetchall()
            self.c.execute('''SELECT checkInMethod from checkIns Where (tribe,
                            date) = (?,?) ''', (tribe, date))
            data = self.c.fetchall()
            if data == []:
                return 0
            else:
                return checkinMethods.index(data[0])

        except Exception:
            self.handle_error()

    def list_checkin_history(self, tribe):
        try:
            self.c.execute('''SELECT date as "date [timestamp]", checkInMethod
                            FROM
                            checkIns WHERE tribe = ?''', (tribe,))
            data = self.c.fetchall()
            return data
        except Exception:
            self.handle_error()

    def get_version(self):
        # provide version and appID info
        try:
            self.c.execute('''SELECT version, appID from meta ''')
            return self.c.fetchall()
        except Exception:
            self.handle_error()

    def add_checkin_method(self, method):
        # Called from main.addCheckMethod adds or removes checkin methods from db
        try:
            self.c.execute('''INSERT into checkInMethods (method) VALUES (?) ''', (method,))
            self.conn.commit()
            # This exception catches user inputs that already exist and deletes them
        # rather than adding them, so a user can delete a checkin this way.
        # A checkin method that has been used cannot be deleted
        except sqlite3.IntegrityError:
            check = self.c.execute('''SELECT tribe FROM checkIns WHERE checkInMethod
                                    = ?''', (method,))
            if len(self.c.fetchall()) > 0:
                return 'cannot delete'
            else:
                self.c.execute('''DELETE FROM checkInMethods WHERE method =
                                (?)''', (method,))
                self.conn.commit()
        except Exception:
            self.handle_error()

    def is_active(self, tribe):
        try:
            self.c.execute('''SELECT Active FROM tribalLocations WHERE
                            tribe = ?''', (tribe,))
            data = self.c.fetchone()
            data = data[0]
            if data == 'True':
                return True
            elif data == 'False':
                return False
        except Exception:
            self.handle_error()

    def make_inactive(self, tribe):
        try:
            self.c.execute('''UPDATE tribalLocations SET Active = 'False'
                            WHERE tribe = ?''', (tribe,))
            self.conn.commit()
        except Exception:
            self.handle_error()

    def makeActive(self, tribe):
        try:
            self.c.execute('''UPDATE tribalLocations SET Active = 'True'
                            WHERE tribe = ?''', (tribe,))
            self.conn.commit()
        except Exception:
            self.handle_error()

    def get_info(self, tribe):
        try:
            self.c.execute('''SELECT information FROM tribalLocations
                            WHERE tribe = ?''', (tribe,))
            data = self.c.fetchone()
            return data[0]
        except Exception:
            self.handle_error()

    def update_info(self, tribe, text):
        try:
            self.c.execute('''UPDATE tribalLocations SET information =  ?
                            WHERE tribe = ?''', (text, tribe))
            self.conn.commit()
        except Exception:
            self.handle_error()

    def delete_location(self, tribe):
        # Called by remove tribe menu item, deletes a tribe from .db including all
        # checkin history (to prevent bugs of trying to access data for a tribe
        # that isn't listed in tribal locations table
        try:
            self.c.execute('''DELETE FROM tribalLocations WHERE tribe = ?''', (tribe,))
            self.c.execute('''DELETE FROM checkIns WHERE tribe = ?''', (tribe,))
            self.conn.commit()
        except Exception:
            self.handle_error()

    def update_family_info(self, new_data, tribe):
        try:
            self.c.execute('''SELECT family FROM tribalLocations WHERE
                            tribe = ?''', (tribe,))
            existing_family_data = self.c.fetchone()[0]

            if existing_family_data != new_data:
                self.c.execute('''UPDATE tribalLocations SET family =?
                                WHERE tribe = ?''', (new_data, tribe))
                self.conn.commit()
        except Exception:
            self.handle_error()

    def get_last_user_action(self):
        try:
            self.c.execute('''SELECT logged as "logged[timestamp]",
                            tribe, checkInMethod FROM checkIns''')
            data = self.c.fetchall()
            data.sort()
            return data[-1]
        except Exception:
            self.handle_error()

    def delete_last(self, timestamp):
        try:
            self.c.execute('''DELETE FROM checkIns WHERE logged = ? ''', (timestamp,))
            self.conn.commit()
        except Exception:
            self.handle_error()

    def close_database(self):
        self.conn.close()
        self.logger.debug('db closed')
        close_logging(self.logger)
