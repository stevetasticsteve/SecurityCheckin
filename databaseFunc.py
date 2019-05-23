import sqlite3
import sys
import logging
import datetime
import csv
import time
from logSettings import createLogger, closeLogging
from SecurityCheckins import version

from PyQt5.QtWidgets import QMessageBox

logger = createLogger(__name__)
logger.addHandler(logging.StreamHandler())

class databaseConnect():

    def __init__(self):
        try:
            self.conn = sqlite3.connect('checkins.db',
                                        detect_types = sqlite3.PARSE_DECLTYPES|
                                        sqlite3.PARSE_COLNAMES)
            self.c = self.conn.cursor()
            self.logger = createLogger(__name__)
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
            

    def handleError(self):
        self.conn.rollback()
        self.logger.exception('Database error, rollback initiated.')
        self.conn.close()
        self.logger.debug('db successfully closed.')
        sys.exit()


    def addTribalLocation(self, name, family):
        try:
            self.c.execute('''INSERT INTO tribalLocations(tribe, family, information, active)
                            VALUES(?, ?, '' ,'True' )''', (name, family))
            self.conn.commit()
        except sqlite3.IntegrityError:
            raise sqlite3.IntegrityError
        except Exception:
            self.handleError()
            

    def listActiveTribalInfo(self):
        try:
            self.c.execute('''SELECT tribe, family FROM tribalLocations
                            WHERE Active = ('True') ''')
            data = self.c.fetchall()
            return data
            #returns a list of tuples (tribe, family units)
        except Exception:
            self.handleError()
            
            
    def listInactiveTribalInfo(self):
        try:
            self.c.execute('''SELECT tribe, family FROM tribalLocations
                            WHERE Active = ('False') ''')
            data = self.c.fetchall()
            return data
            #returns a list of tuples (tribe, family units)
        except Exception:
            self.handleError()
            
            
    def listAllTribalLocations(self):
    # This function returns a list of both active and inactive works
        try:
            active = self.listActiveTribalInfo()
            inactive = self.listInactiveTribalInfo()
            tribalLocations = []
            for tup in active:
                tribalLocations.append(tup)
            for tup in inactive:
                tribalLocations.append(tup)
            return tribalLocations
            # returns a list of tuples (tribe, family units) active + inactive
        except Exception:
            self.handleError()
            

    def listCheckinMethods(self):
        try:
            self.c.execute('''SELECT method FROM checkInMethods ''')
            return self.c.fetchall()
        except Exception:
            self.handleError()
            

    def logCheckIn(self, tribe, method, date):
        try:
            self.c.execute('''SELECT date as "date [timestamp]"
                            FROM checkIns WHERE tribe = ?''', (tribe, ))
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
            self.handleError()
            

    def getLastCheckIn(self, tribe):
        try:
            self.c.execute('''SELECT date as "date [timestamp]"
                            FROM checkIns WHERE tribe = ? ''',(tribe, ))
            data = self.c.fetchall()
            if data == []:
                return 'n/a'
            latestCheckIn = max(data)
            return latestCheckIn[0]
        except Exception:
            self.handleError()
            
            
    def sortTribesByLastCheckin(self):
    #Used to get all active tribal locations sorted by date of last checkin,
    #used in the drawActiveWidget function
        try:
            activeTribes = self.c.execute('''SELECT tribe, family FROM
                                            tribalLocations
                                            WHERE Active = ('True') ''')
            data = self.c.fetchall()
            tribes = []
            #Use the tribe name to retrive it's last checkin datetime
            #and add it at index 0
            for tup in data:
                tup = list(tup)
                tup.insert(0, self.getLastCheckIn(tup[0]))
                #If tribe not checked in ever 'n/a' will crash the sort
                if type(tup[0]) == str:
                    tup[0] = datetime.datetime.now()
                tribes.append(tup)
            #sort by datetime
            tribes.sort()
            #remove the datetime object
            for tup in tribes:
                tup.remove(tup[0])
            #return a list of lists (tribe, family)
            return(tribes)
        except Exception:
            self.handleError()
            
            
    def sortAlphabetically(self):
    #Used to get all active tribal locations sorted alphabetically,
    #used in the drawActiveWidget function
        try:
            activeTribes = self.c.execute('''SELECT tribe, family FROM
                                            tribalLocations
                                            WHERE Active = ('True') ''')
            data = self.c.fetchall()
            tribes = []
            #convert into a list of lists
            for tup in data:
                tup = list(tup)
                tribes.append(tup)
            #sort alphabetically
            tribes.sort()
            #returns a list of lists
            return tribes
        except Exception:
            self.handleError()
            
            
    def getLastCheckinMethod(self, tribe):
        try:
            date = self.getLastCheckIn(tribe)
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
            self.handleError()
            

    def listCheckinHistory(self, tribe):
        try:
            self.c.execute('''SELECT date as "date [timestamp]", checkInMethod
                            FROM
                            checkIns WHERE tribe = ?''', (tribe, ))
            data = self.c.fetchall()
            return data
        except Exception:
            self.handleError()

            
    def getVersion(self):
    # provide version and appID info
        try:
            self.c.execute('''SELECT version, appID from meta ''')
            version = self.c.fetchall()
            return version
        except Exception:
            self.handleError()
            

    def addCheckinMethod(self, method):
    # Called from main.addCheckMethod adds or removes checkin methods from db
        try:
            self.c.execute('''INSERT into checkInMethods (method) VALUES (?) ''', (method,))
            self.conn.commit()            
        # This exception catches user inputs that already exist and deletes them
        # rather than adding them, so a user can delete a checkin this way.
        # A checkin method that has been used cannot be deleted
        except sqlite3.IntegrityError:
            check = self.c.execute('''SELECT tribe FROM checkIns WHERE checkInMethod
                                    = ?''', (method, ))
            if len(self.c.fetchall()) > 0:
                return 'cannot delete'
            else:
                self.c.execute('''DELETE FROM checkInMethods WHERE method =
                                (?)''', (method, ))
                self.conn.commit()
        except Exception:
            self.handleError()
            

    def isActive(self, tribe):
        try:
            self.c.execute('''SELECT Active FROM tribalLocations WHERE
                            tribe = ?''', (tribe, ))
            data = self.c.fetchone()
            data = data[0]
            if data == 'True':
                return True
            elif data == 'False':
                return False
        except Exception:
            self.handleError()
            

    def makeInactive(self, tribe):
        try:
            self.c.execute('''UPDATE tribalLocations SET Active = 'False'
                            WHERE tribe = ?''', (tribe,))
            self.conn.commit()
        except Exception:
            self.handleError()
            

    def makeActive(self, tribe):
        try:
            self.c.execute('''UPDATE tribalLocations SET Active = 'True'
                            WHERE tribe = ?''', (tribe,))
            self.conn.commit()
        except Exception:
            self.handleError()
            

    def getInfo(self, tribe):
        try:
            self.c.execute('''SELECT information FROM tribalLocations
                            WHERE tribe = ?''', (tribe, ))
            data = self.c.fetchone()
            return data[0]
        except Exception:
            self.handleError()
            

    def updateInfo(self, tribe, text):
        try:
            self.c.execute('''UPDATE tribalLocations SET information =  ?
                            WHERE tribe = ?''', (text, tribe))
            self.conn.commit()
        except Exception:
            self.handleError()
            

    def deleteLocation(self, tribe):
    #Called by remove tribe menu item, deletes a tribe from .db including all
    #checkin history (to prevent bugs of trying to access data for a tribe
    #that isn't listed in tribal locations table
        try:
            self.c.execute('''DELETE FROM tribalLocations WHERE tribe = ?''', (tribe, ))
            self.c.execute('''DELETE FROM checkIns WHERE tribe = ?''', (tribe, ))
            self.conn.commit()
        except Exception:
            self.handleError()
            

    def updateFamilyInfo(self, newData, tribe):
        try:
            self.c.execute('''SELECT family FROM tribalLocations WHERE
                            tribe = ?''', (tribe, ))
            existingFamilyData = self.c.fetchone()[0]

            if existingFamilyData != newData:
                self.c.execute('''UPDATE tribalLocations SET family =?
                                WHERE tribe = ?''', (newData, tribe))
                self.conn.commit()
        except Exception:
            self.handleError()
            

    def getLastUserAction(self):
        try:          
            self.c.execute('''SELECT logged as "logged[timestamp]",
                            tribe, checkInMethod FROM checkIns''')
            data = self.c.fetchall()
            data.sort()
            return data[-1]
        except Exception:
            self.handleError()
            

    def deleteLast(self, timestamp):
        try:
            self.c.execute('''DELETE FROM checkIns WHERE logged = ? ''', (timestamp, ))
            self.conn.commit()
        except Exception:
            self.handleError()

                       
    def closeDatabase(self):
        self.conn.close()
        self.logger.debug('db closed')
        closeLogging(self.logger)

