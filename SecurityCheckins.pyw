import sys
import os
import logging
import datetime
import shutil
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QPushButton
from PyQt5.QtWidgets import QLabel, QScrollArea, QComboBox, QCalendarWidget
from PyQt5.QtWidgets import QWidget, QGridLayout, QDateEdit, QDialog, QLineEdit
from PyQt5.QtWidgets import QInputDialog
from PyQt5 import QtGui
import UI.checkinUI
import function.logSettings
import function.databaseFunc
import UI.EditDbDialog
import UI.checkinCalendarScreen
import UI.aboutScreen
import UI.activeScreen
import UI.infoScreen


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = UI.checkinUI.Ui_MainWindow()
        self.setWindowIcon(QtGui.QIcon(resource_path('CheckinIcon.ico')))
        self.ui.setupUi(self)
        self.resize(1000,900)
        self.statusBar = self.ui.statusbar
        #Join menu items to functions
        self.ui.actionExit.triggered.connect(self.close)
        self.ui.actionAbout.triggered.connect(self.about)
        self.ui.actionAdd_Remove_checkin_methods.triggered.connect(self.addCheckMethod)
        self.ui.actionHelp_contents.triggered.connect(self.helpContents)
        self.ui.actionSet_active_inactive.triggered.connect(self.setActiveInactive)
        self.ui.actionLast_check_in_order.triggered.connect(self.changeOrder)
        self.ui.actionAlphabetical_order.triggered.connect(self.changeOrder)
        self.ui.actionRemove_tribe.triggered.connect(self.removeTribeDialog)
        self.ui.actionAdd_tribe.triggered.connect(self.addTribe)
        self.ui.actionEdit_family_information.triggered.connect(self.editFamilyInfo)
        self.ui.actionUndo_last_checkin.triggered.connect(self.undoLast)
        #Initialize window
        self.grid = self.ui.gridLayout_2
        self.show

    def home(self, db):
        logger.debug('GUI (re)drawn')
        self.db = db
        # create active subwidget with grid layout      
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.activeWidget = QWidget()
        self.activeGrid = QGridLayout()
        self.activeWidget.setLayout(self.activeGrid)
        self.scrollArea2 = QScrollArea()
        self.inactiveWidget = QWidget()
        self.inactiveGrid = QGridLayout()
        self.inactiveWidget.setLayout(self.inactiveGrid)
        self.activeTribalLocations = []
        self.activeTribalFamilies = []
        self.inactiveTribalLocations = []
        self.inactiveTribalFamilies = []
        if hasattr(self, 'userDate') == False: # only use today if user not set date
            self.userDate = datetime.datetime.now()
        self.dateEdit = QDateEdit(self.userDate)
        self.dateEdit.setMaximumDate(datetime.datetime.now())
        self.dateEdit.setMinimumDate(datetime.date(2018,1,1))
        self.dateEdit.setCalendarPopup(True)
        self.pickDateLbl = QLabel('Select checkin date')
        self.activeLbl = QLabel('Active works')
        self.inactiveLbl = QLabel('Inactive works')   
        # populate active and inactive sub-widgets
        i = self.drawActiveWidget()
        i = i + 10 # prevents problems if only 0-1 tribes are active
        self.drawInactiveWidget(self.db.listInactiveTribalInfo())
        # Add widgets to grid of main window    
        self.grid.addWidget(self.pickDateLbl, 0, 1,)
        self.grid.addWidget(self.dateEdit, 0, 2)
        self.grid.addWidget(self.activeLbl, 1, 0)
        self.grid.addWidget(self.scrollArea, 2, 0, 2, 5)
        self.scrollArea.setWidget(self.activeWidget)
        self.grid.addWidget(self.inactiveLbl, i + 1, 0) #i+1 stops widgets drawing over other widgets
        self.grid.addWidget(self.scrollArea2, i + 2, 0, i + 2, 5)
        self.scrollArea2.setWidget(self.inactiveWidget)
        

    def drawActiveWidget(self):
    #called as part of the home function, adds labels and buttons for each
    #active tribal location in the active sub widget
        if  self.ui.actionLast_check_in_order.isChecked():
            tribalLocations = self.db.sortTribesByLastCheckin()
        elif  self.ui.actionAlphabetical_order.isChecked():
            tribalLocations = self.db.sortAlphabetically()
        #split the list of lists into 2 lists
        for tribe in tribalLocations:
            self.activeTribalLocations.append(tribe[0])
            self.activeTribalFamilies.append(tribe[1])
        self.tribeBtn = []
        self.familyLbl = []
        self.checkInBtn = []
        self.lastCheckIn = []
        self.checkInCombo = []
        self.infoBtn = []
        j = 0 #temp variable that will only return if no active tribes
        for i, tribe in enumerate(self.activeTribalLocations):
            j = i +1
            tribeBtn = QPushButton(tribe)
            tribeBtn.setFlat(True)
            tribeBtn.setFont(QtGui.QFont("Times",weight=QtGui.QFont.Bold))
            tribeBtn.setMaximumWidth(150)
            self.tribeBtn.append(tribeBtn)
            self.tribeBtn[i].clicked.connect(
                lambda: self.showCalendar(self.sender().text()))
            familyLbl = QLabel(self.activeTribalFamilies[i])
            self.familyLbl.append(familyLbl)
            lastCheckLbl = QLabel()
            lastCheckLbl.setMaximumWidth(60)
            self.updateLastCheckInLabel(lastCheckLbl, tribe)
            self.lastCheckIn.append(lastCheckLbl)
            checkInBtn = QPushButton(tribe + ' Checkin')
            self.checkInBtn.append(checkInBtn)
            self.checkInBtn[i].clicked.connect(
                lambda: self.checkIn(self.sender().text()))
            self.populateComboBoxes()
            infoBtn = QPushButton()
            infoBtn.setMaximumWidth(30)
            infoBtn.setFlat(True)
            infoBtn.setObjectName(tribe + ' info btn')
            infoBtn.setIcon(QtGui.QIcon(resource_path('Info-icon.png')))
            self.infoBtn.append(infoBtn)
            self.infoBtn[i].clicked.connect(
                lambda: self.seeInfo(self.sender().objectName()))
            self.activeGrid.addWidget(tribeBtn, (j), 0)
            self.activeGrid.addWidget(lastCheckLbl, (j), 3)
            self.activeGrid.addWidget(self.checkInCombo[i], (j), 4)
            self.activeGrid.addWidget(checkInBtn, (j), 5)
            self.activeGrid.addWidget(familyLbl, (j), 2)
            self.activeGrid.addWidget(infoBtn, j, 1)
        #returns an integer of number of rows required
        return j
    

    def drawInactiveWidget(self, inactiveTribeList):
    # create a widget (as container) with inactive works presented.
        self.inactiveInfoBtn = []
        for tribe in inactiveTribeList:
            self.inactiveTribalLocations.append(tribe[0])
            self.inactiveTribalFamilies.append(tribe[1])

        for i, tribe in enumerate(self.inactiveTribalLocations):
            tribeLbl = QLabel(self.inactiveTribalLocations[i])
            tribeLbl.setFont(QtGui.QFont("Times",weight=QtGui.QFont.Bold))
            familyLbl = QLabel(self.inactiveTribalFamilies[i])
            spacer = QLabel('|')
            infoBtn = QPushButton()
            infoBtn.setObjectName(tribe + ' info btn')
            infoBtn.setMaximumWidth(30)
            infoBtn.setFlat(True)
            infoBtn.setObjectName(tribe + ' info btn')
            infoBtn.setIcon(QtGui.QIcon('Info-icon.png'))
            self.inactiveInfoBtn.append(infoBtn)
            self.inactiveInfoBtn[i].clicked.connect(
                lambda: self.seeInfo(self.sender().objectName()))

            self.inactiveGrid.addWidget(tribeLbl, i, 0)
            self.inactiveGrid.addWidget(spacer, i, 2)
            self.inactiveGrid.addWidget(familyLbl, i, 3)
            self.inactiveGrid.addWidget(infoBtn, i, 1)


    def handleError(self):
    # provides a message box when errors happen. It's not called for every
    # function (my laziness) but being put into the resetScreen() exception
    # loop covers most eventualities as it's called so often.
        logger.exception('Fatal Error:')
        QMessageBox.about(self, 'Error', 'A fatal error has occured, '
                              'check the log for details', )
        sys.exit()


    def closeEvent(self, event):
    # action taken when window is closed (any way), ensures .db is closed well
        try:
            logger.debug('Close event')
            try:
                self.db.closeDatabase()
            except AttributeError: #in case no .db exists program can still close
                pass
            function.logSettings.closeLogging(logger)
            app.quit()
        except Exception:
            self.handleError()
            

    def checkIn(self, name):
    # when checkin button pressed log info into .db
        try:
            qdate = self.dateEdit.date()
            self.userDate = qdate # overides if condition in home
            date = datetime.datetime(qdate.year(), qdate.month(), qdate.day(), 0)
            index = self.checkInBtn.index(self.sender())
            name = name.rstrip('Checkin')
            name = name.rstrip(' ')
            method = self.checkInCombo[index].currentText()
            ret = self.db.logCheckIn(name, method, date)
            if ret == 'Already checked in':
                self.statusBar.showMessage(name +
                                           ' already checked in on'
                                           ' specified date')
            else:
                self.updateLastCheckInLabel(self.lastCheckIn[index], name)
                self.statusBar.showMessage('Logged ' + name +
                                       ' as checked in via ' + method, 4000)
                self.resetScreen() #causes tribe to jump to bottom when ordered by checkin
            
        except Exception:
            self.handleError()
        
    def updateLastCheckInLabel(self, label, tribe):
    # sets how many days since check in label, colours it red 4 days or up
        try:
            lastCheckIn = self.db.getLastCheckIn(tribe)
            if lastCheckIn == 'n/a':
                label.setText('n/a')
                return
            delta = datetime.datetime.now() - lastCheckIn
            deltadays = delta.days
            label.setText(str(deltadays) + ' days')

            if deltadays > 3:
                label.setStyleSheet("QLabel { color: red}")
            else:
                label.setStyleSheet("QLabel { color: black}")
            self.update()
        except Exception:
            self.handleError()
            
            
    def showCalendar(self, tribe):
    # pulls up calendar when tribe name pressed (see UI.checkinCalendarScreen.py)
        UI.checkinCalendarScreen.calendarWidget(w, tribe, self.db)
        

    def about(self):
        logger.debug('about function called')
    # pulls about about widget see about.py
        UI.aboutScreen.aboutWidget(w, self.db)
        

    def helpContents(self):
        logger.debug('helpContents function called')
    # pulls up instruction manual
        pass

    
    def resetScreen(self):
    # Causes main widget to redraw, used to keep widget current with .db changes
        try:
            for i in reversed(range(1, self.grid.count())):
                self.grid.itemAt(i).widget().setParent(None)
            self.home(self.db)
        except Exception:
            self.handleError()
            

    def addCheckMethod(self):
        logger.debug('addCheckMethod function called')
    # produces an input dialog that takes text and uses it to either create a
    # checkin method if it doesn't exist or delete it if it does
    # called from a menu item
        newMethod, ok = QInputDialog.getText(self, 'Add/remove checkin method',
                                            'Enter new check in method. If you'
                                             ' enter one that already exists it'
                                             ' will be deleted instead')
        if ok and newMethod:
            try:
                func = self.db.addCheckinMethod(newMethod)
                if func == 'cannot delete':
                    msg = QMessageBox.about(self, 'Cannot delete',
                                            'Checkin method is being used'
                                            ' in db and cannot be deleted')
                    return
                self.resetScreen()
            except Exception:
                logger.exception('addCheckMethod fail')
        

    def populateComboBoxes(self):
    # gets a list of checkin methods from db and then fills a combo box, setting
    # the lastcheckin is the active option. Called for each combo box
    # during drawActiveWidget func
        checkinMethods = self.db.listCheckinMethods()
        for tribe in self.activeTribalLocations:
            combo = QComboBox()
            for method in checkinMethods:
                combo.addItem(method[0])
            self.checkInCombo.append(combo)
            last = self.db.getLastCheckinMethod(tribe)
            combo.setCurrentIndex(last)
            

    def setActiveInactive(self):
        logger.debug('setActiveInactive function called')
    # Pulls up a new window featuring checkboxes where active and inactive can
    # be set (see UI.infoScreen.py) called from a menu item
        UI.activeScreen.UI.activeScreenWidget(w, self.db)
        

    def seeInfo(self, tribe):
        logger.debug('seeInfo function called')
    # Pulls up a new window in which to write notes (see UI.infoScreen.py)
    # Called from a menu item
        tribe = tribe.rstrip(' btn')
        tribe = tribe.rstrip('info')
        tribe = tribe.rstrip(' ')
        UI.infoScreen.UI.infoScreenWidget(w, self.db, tribe)
        

    def changeOrder(self):
        logger.debug('changeOrder function called')
    # Sets the other order menu item to unchecked and redraws main window.
    # Called from menu items
        sender = self.sender().objectName()
        if  sender == 'actionLast_check_in_order':
            self.ui.actionAlphabetical_order.setChecked(False)
        elif  sender == 'actionAlphabetical_order':
            self.ui.actionLast_check_in_order.setChecked(False)
        self.resetScreen()
        

    def removeTribeDialog(self):
        logger.debug('removeTribeDialog function called')
        # Called by menu option pulls up a message box explaining function,
        # then creates a dialog with combo box to select tribe to delete to pass
        # to removeTribe function
        try:
            msg = QMessageBox.question(self, 'Really remove?',
                                      'This function will delete the tribal '
                                      'location and all checkin information '
                                      'from the .db. This is to completely '
                                      'and totally delete a work. If you want '
                                      'to keep the work listed make it inactive'
                                      ' instead. Do you want to continue?')
            # Only continue if user understands and agrees to delete
            if msg == QMessageBox.Yes:
                logger.info('User agreed to delete tribal location')
                # Create dialog
                self.removeDialog = QDialog(w)
                self.removeDialog.setFixedSize(200, 200)
                self.removeDialog.setWindowTitle('Remove a tribal location')
                grid = QGridLayout()
                self.removeCombo = QComboBox()
                #Get list of all tribal locations
                tribes = self.db.listAllTribalLocations()
                self.tribesList = []
                for tribe in tribes:
                    self.removeCombo.addItem(tribe[0])
                    self.tribesList.append(tribe[0])
                # Create button and connect it to removeTribe function
                btn = QPushButton('Ok')
                btn.pressed.connect(self.removeTribe)
                # Cancel button
                cancelBtn = QPushButton('Cancel')
                cancelBtn.pressed.connect(self.removeDialog.close)
                # Add widgets to Grid and show dialog
                grid.addWidget(self.removeCombo, 0, 0, 0, 2)
                grid.addWidget(btn, 1, 0)
                grid.addWidget(cancelBtn, 1 ,1)
                self.removeDialog.setLayout(grid)
                self.removeDialog.show()
        except Exception:
                logger.exception('removeTribe fail')


    def removeTribe(self):
        logger.debug('removeTribe function called')
    #Called when Ok clicked in remove tribe dialog. Gets current tribe in combo
    #box and deletes it completely from .db
        try:
            tribe = self.tribesList[self.removeCombo.currentIndex()]
            self.db.deleteLocation(tribe)
            msg = QMessageBox.about(self, 'Done', tribe + ' deleted from .db')
            self.removeDialog.close()
            self.resetScreen()
        except Exception:
                logger.exception('removeTribe fail')


    def addTribe(self):
        logger.debug('addTribe function called')
    # called by a menu item, pulls up an input dialog to take the name of a 
    # tribe to add to the .db
        try:
            newTribe , ok = QInputDialog.getText(self, 'Add Tribe',
                                                'Enter name of new '
                                                 'Tribal Location')
            if ok and newTribe:
                # Create new .db row with family blank to be filled in later
                self.db.addTribalLocation(newTribe, '')
                self.resetScreen()
        except Exception:
                logger.exception('addTribe fail')
                

    def editFamilyInfo(self):
        logger.debug('editFamilyInfo function called')
    # Called by the menu item, pulls up the family info for the selected tribe
    # which can be edited by the user
        try:
            # Get dialog layout ready
            self.editFamilyDialog = QDialog(w)
            self.editFamilyDialog.setWindowTitle('Edit family information')
            self.editFamilyDialog.resize(500,800)
            editFamilyWidget = QWidget()
            scrollArea = QScrollArea()
            grid = QGridLayout()
            editGrid = QGridLayout()
            # Get active and inactive tribal locations
            text = self.db.listAllTribalLocations()
            self.FEtribeLabels = []
            self.familyLineEdits = []
            # Fill a widget with labels and line edits
            for i, tribe in enumerate(text):
                lbl = QLabel(tribe[0])
                self.FEtribeLabels.append(lbl)
                lineEdit = QLineEdit(tribe[1])
                lineEdit.setMinimumWidth(300)
                self.familyLineEdits.append(lineEdit)
                editGrid.addWidget(lbl, i, 0)
                editGrid.addWidget(lineEdit, i, 1)
            # Create Ok button set to trigger updateFamilies function
            okBtn = QPushButton('Ok')
            okBtn.pressed.connect(self.updateFamilies)
            # Place everything on a grid
            editGrid.addWidget(okBtn, i + 1 , 1)
            grid.addWidget(scrollArea)
            editFamilyWidget.setLayout(editGrid)
            self.editFamilyDialog.setLayout(grid)
            scrollArea.setWidget(editFamilyWidget)
            self.editFamilyDialog.show()
        except Exception:
            logger.exception('editFamilyInfo fail')
            

    def updateFamilies(self):
        logger.debug('updateFamilies function called')
    # Called from editFamilyInfo function, closes dialog and updates .db
        for i, item in enumerate(self.familyLineEdits):
            self.db.updateFamilyInfo(item.text(), self.FEtribeLabels[i].text())
        self.editFamilyDialog.close()
        self.resetScreen()
        

    def undoLast(self):
        logger.debug('undoLast function called')
    # Called froma  menu item, finds last checkin, shows info in a message box
    # and asks for confirmation to delete from .db. Used to fix user misclicks
        try:
            checkin = self.db.getLastUserAction()
            checkinInfo = checkin[1] + ' who checked in by ' + checkin[2]
            msg = QMessageBox.question(w,
                                       'Delete last checkin',
                                       'The last checkin was: ' + checkinInfo +
                                       ' do you really want to delete this from .db?')
            if msg == QMessageBox.Yes:
                self.db.deleteLast(checkin[0])
                self.resetScreen()
        except Exception:
            logger.exception('undoLast function fail')       
    
if __name__ == '__main__':
    # small code snippet to help pyinstaller find images. Does nothing outside
    # pyinstaller runtime
    def resource_path(relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath('.'), relative_path)
    
    # Start logging
    logger = function.logSettings.createLogger(__name__)
    logger.addHandler(logging.StreamHandler())
    logger.info('GUI started')
    # Create GUI process
    app = QApplication(sys.argv)
    w = MyApp()
    w.show()
    # Check if .db exists or not. If not create it or load one before continuing
    # Should only execute on first use of program.
    if os.path.exists('checkins.db') == False:
        logger.info('No .db exists, program must be running for first time')
        # Create custom message box
        msgBox = QMessageBox()
        msgBox.setText('No database detected,'
                       'do you want to create one or load one?')
        msgBox.setWindowTitle('No database detected')
        msgBox.setIcon(QMessageBox.Question)
        msgBox.addButton(QPushButton('Create'), QMessageBox.YesRole)
        msgBox.addButton(QPushButton('Load'), QMessageBox.NoRole)
        # Execute in a way that program waits for response
        ret = msgBox.exec_()
        if ret == 0:
            logger.info('User chose to create new .db')
            UI.EditDbDialog.createDBDialog(w).exec_()
        elif ret == 1:
        # Pull up a open file window if load called. Copy selected .db to
        # cwd, which should be the application folder
            logger.info('User chose to load existing .db')
            file = UI.EditDbDialog.loadDB(w)
            if file:
                shutil.copyfile(file, 'checkins.db')
                QMessageBox.about(w,
                                  'File copy complete', 
                                  'Db has been copied to application folder, '
                                  'you can delete the original if you like.')
            else:
                msg = QMessageBox.warning(w,
                                        'Error',
                                        "You didn't select a valid database")
                if msg:
                    w.close()
                    sys.exit()
            
    # If .db already exists connect to .db and run program. Should run always
    # after initial setup
    if os.path.exists('checkins.db'):
        x = w.home(function.databaseFunc.databaseConnect())
    sys.exit(app.exec_())
