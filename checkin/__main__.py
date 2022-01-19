import datetime
import logging
import os
import shutil
import sys
from importlib import resources

from PyQt5 import QtGui
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QLabel, QScrollArea, QComboBox
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QPushButton
from PyQt5.QtWidgets import QWidget, QGridLayout, QDateEdit, QDialog, QLineEdit

from checkin.UI import aboutScreen 
from checkin.UI import activeScreen 
from checkin.UI import checkinCalendarScreen 
from checkin.UI import checkinUI
from checkin.UI import infoScreen 
from checkin.UI import EditDbDialog 
from checkin.function import databaseFunc
from checkin.function import logSettings


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = checkinUI.Ui_MainWindow()
        with resources.path("checkin.icons", "CheckinIcon.ico") as path:
            self.setWindowIcon(QtGui.QIcon(resource_path(path)))
        self.ui.setupUi(self)
        self.resize(1000, 900)
        self.statusBar = self.ui.statusbar
        # Join menu items to functions
        self.ui.actionExit.triggered.connect(self.close)
        self.ui.actionAbout.triggered.connect(self.about)
        self.ui.actionAdd_Remove_checkin_methods.triggered.connect(self.add_check_method)
        self.ui.actionHelp_contents.triggered.connect(self.helpContents)
        self.ui.actionSet_active_inactive.triggered.connect(self.set_active_inactive)
        self.ui.actionLast_check_in_order.triggered.connect(self.change_order)
        self.ui.actionAlphabetical_order.triggered.connect(self.change_order)
        self.ui.actionRemove_tribe.triggered.connect(self.remove_tribe_dialog)
        self.ui.actionAdd_tribe.triggered.connect(self.add_tribe)
        self.ui.actionEdit_family_information.triggered.connect(self.edit_family_info)
        self.ui.actionUndo_last_checkin.triggered.connect(self.undo_last)
        # Initialize window
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
        if hasattr(self, 'userDate') == False:  # only use today if user not set date
            self.userDate = datetime.datetime.now()
        self.dateEdit = QDateEdit(self.userDate)
        self.dateEdit.setMaximumDate(datetime.datetime.now())
        self.dateEdit.setMinimumDate(datetime.date(2018, 1, 1))
        self.dateEdit.setCalendarPopup(True)
        self.pickDateLbl = QLabel('Select checkin date')
        self.activeLbl = QLabel('Active works')
        self.inactiveLbl = QLabel('Inactive works')
        # populate active and inactive sub-widgets
        i = self.draw_active_widget()
        i = i + 10  # prevents problems if only 0-1 tribes are active
        self.draw_inactive_widget(self.db.list_inactive_tribal_info())
        # Add widgets to grid of main window    
        self.grid.addWidget(self.pickDateLbl, 0, 1, )
        self.grid.addWidget(self.dateEdit, 0, 2)
        self.grid.addWidget(self.activeLbl, 1, 0)
        self.grid.addWidget(self.scrollArea, 2, 0, 2, 5)
        self.scrollArea.setWidget(self.activeWidget)
        self.grid.addWidget(self.inactiveLbl, i + 1, 0)  # i+1 stops widgets drawing over other widgets
        self.grid.addWidget(self.scrollArea2, i + 2, 0, i + 2, 5)
        self.scrollArea2.setWidget(self.inactiveWidget)

    def draw_active_widget(self):
        # called as part of the home function, adds labels and buttons for each
        # active tribal location in the active sub widget
        if self.ui.actionLast_check_in_order.isChecked():
            tribal_locations = self.db.sort_tribes_by_last_checkin()
        elif self.ui.actionAlphabetical_order.isChecked():
            tribal_locations = self.db.sort_alphabetically()
        # split the list of lists into 2 lists
        for tribe in tribal_locations:
            self.activeTribalLocations.append(tribe[0])
            self.activeTribalFamilies.append(tribe[1])
        self.tribe_btn = []
        self.family_lbl = []
        self.check_in_btn = []
        self.last_check_in = []
        self.check_in_combo = []
        self.info_btn = []
        j = 0  # temp variable that will only return if no active tribes
        for i, tribe in enumerate(self.activeTribalLocations):
            j = i + 1
            tribe_btn = QPushButton(tribe)
            tribe_btn.setFlat(True)
            tribe_btn.setFont(QtGui.QFont("Times", weight=QtGui.QFont.Bold))
            tribe_btn.setMaximumWidth(150)
            self.tribe_btn.append(tribe_btn)
            self.tribe_btn[i].clicked.connect(
                lambda: self.show_calendar(self.sender().text()))
            family_lbl = QLabel(self.activeTribalFamilies[i])
            self.family_lbl.append(family_lbl)
            last_check_lbl = QLabel()
            last_check_lbl.setMaximumWidth(60)
            self.update_last_check_in_label(last_check_lbl, tribe)
            self.last_check_in.append(last_check_lbl)
            check_in_btn = QPushButton(tribe + ' Checkin')
            self.check_in_btn.append(check_in_btn)
            self.check_in_btn[i].clicked.connect(
                lambda: self.check_in(self.sender().text()))
            self.populate_combo_boxes()
            info_btn = QPushButton()
            info_btn.setMaximumWidth(30)
            info_btn.setFlat(True)
            info_btn.setObjectName(tribe + ' info btn')
            with resources.path("checkin.icons", "Info-icon.png") as path:
                info_btn.setIcon(QtGui.QIcon(resource_path(path)))
            self.info_btn.append(info_btn)
            self.info_btn[i].clicked.connect(
                lambda: self.see_info(self.sender().objectName()))
            self.activeGrid.addWidget(tribe_btn, (j), 0)
            self.activeGrid.addWidget(last_check_lbl, (j), 3)
            self.activeGrid.addWidget(self.check_in_combo[i], (j), 4)
            self.activeGrid.addWidget(check_in_btn, (j), 5)
            self.activeGrid.addWidget(family_lbl, (j), 2)
            self.activeGrid.addWidget(info_btn, j, 1)
        # returns an integer of number of rows required
        return j

    def draw_inactive_widget(self, inactive_tribe_list):
        # create a widget (as container) with inactive works presented.
        self.inactive_info_btn = []
        for tribe in inactive_tribe_list:
            self.inactiveTribalLocations.append(tribe[0])
            self.inactiveTribalFamilies.append(tribe[1])

        for i, tribe in enumerate(self.inactiveTribalLocations):
            tribe_lbl = QLabel(self.inactiveTribalLocations[i])
            tribe_lbl.setFont(QtGui.QFont("Times", weight=QtGui.QFont.Bold))
            family_lbl = QLabel(self.inactiveTribalFamilies[i])
            spacer = QLabel('|')
            info_btn = QPushButton()
            info_btn.setObjectName(tribe + ' info btn')
            info_btn.setMaximumWidth(30)
            info_btn.setFlat(True)
            info_btn.setObjectName(tribe + ' info btn')
            with resources.path("checkin.icons", "Info-icon.png") as path:
                info_btn.setIcon(QtGui.QIcon(path))
            self.inactive_info_btn.append(info_btn)
            self.inactive_info_btn[i].clicked.connect(
                lambda: self.see_info(self.sender().objectName()))

            self.inactiveGrid.addWidget(tribe_lbl, i, 0)
            self.inactiveGrid.addWidget(spacer, i, 2)
            self.inactiveGrid.addWidget(family_lbl, i, 3)
            self.inactiveGrid.addWidget(info_btn, i, 1)

    def handle_error(self):
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
                self.db.close_database()
            except AttributeError:  # in case no .db exists program can still close
                pass
            logSettings.close_logging(logger)
            app.quit()
        except Exception:
            self.handle_error()

    def check_in(self, name):
        # when checkin button pressed log info into .db
        try:
            qdate = self.dateEdit.date()
            self.userDate = qdate  # overides if condition in home
            date = datetime.datetime(qdate.year(), qdate.month(), qdate.day(), 0)
            index = self.check_in_btn.index(self.sender())
            name = name.rstrip('Checkin')
            name = name.rstrip(' ')
            method = self.check_in_combo[index].currentText()
            ret = self.db.log_check_in(name, method, date)
            if ret == 'Already checked in':
                self.statusBar.showMessage(name +
                                           ' already checked in on'
                                           ' specified date')
            else:
                self.update_last_check_in_label(self.last_check_in[index], name)
                self.statusBar.showMessage('Logged ' + name +
                                           ' as checked in via ' + method, 4000)
                self.resetScreen()  # causes tribe to jump to bottom when ordered by checkin

        except Exception:
            self.handle_error()

    def update_last_check_in_label(self, label, tribe):
        # sets how many days since check in label, colours it red 4 days or up
        try:
            last_check_in = self.db.get_last_check_in(tribe)
            if last_check_in == 'n/a':
                label.setText('n/a')
                return
            delta = datetime.datetime.now() - last_check_in
            deltadays = delta.days
            label.setText(str(deltadays) + ' days')

            if deltadays > 3:
                label.setStyleSheet("QLabel { color: red}")
            else:
                label.setStyleSheet("QLabel { color: black}")
            self.update()
        except Exception:
            self.handle_error()

    def show_calendar(self, tribe):
        # pulls up calendar when tribe name pressed (see checkinCalendarScreen.py)
        checkinCalendarScreen.CalendarWidget(w, tribe, self.db)

    def about(self):
        logger.debug('about function called')
        # pulls about about widget see about.py
        aboutScreen.AboutWidget(w, self.db)

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
            self.handle_error()

    def add_check_method(self):
        logger.debug('addCheckMethod function called')
        # produces an input dialog that takes text and uses it to either create a
        # checkin method if it doesn't exist or delete it if it does
        # called from a menu item
        new_method, ok = QInputDialog.getText(self, 'Add/remove checkin method',
                                             'Enter new check in method. If you'
                                             ' enter one that already exists it'
                                             ' will be deleted instead')
        if ok and new_method:
            try:
                func = self.db.add_checkin_method(new_method)
                if func == 'cannot delete':
                    msg = QMessageBox.about(self, 'Cannot delete',
                                            'Checkin method is being used'
                                            ' in db and cannot be deleted')
                    return
                self.resetScreen()
            except Exception:
                logger.exception('addCheckMethod fail')

    def populate_combo_boxes(self):
        # gets a list of checkin methods from db and then fills a combo box, setting
        # the lastcheckin is the active option. Called for each combo box
        # during drawActiveWidget func
        checkin_methods = self.db.list_checkin_methods()
        for tribe in self.activeTribalLocations:
            combo = QComboBox()
            for method in checkin_methods:
                combo.addItem(method[0])
            self.check_in_combo.append(combo)
            last = self.db.get_last_checkin_method(tribe)
            combo.setCurrentIndex(last)

    def set_active_inactive(self):
        logger.debug('setActiveInactive function called')
        # Pulls up a new window featuring checkboxes where active and inactive can
        # be set (see infoScreen.py) called from a menu item
        activeScreen.Activescreenwidget(w, self.db)

    def see_info(self, tribe):
        logger.debug('seeInfo function called')
        # Pulls up a new window in which to write notes (see infoScreen.py)
        # Called from a menu item
        tribe = tribe.rstrip(' btn')
        tribe = tribe.rstrip('info')
        tribe = tribe.rstrip(' ')
        infoScreen.InfoScreenWidget(w, self.db, tribe)

    def change_order(self):
        logger.debug('changeOrder function called')
        # Sets the other order menu item to unchecked and redraws main window.
        # Called from menu items
        sender = self.sender().objectName()
        if sender == 'actionLast_check_in_order':
            self.ui.actionAlphabetical_order.setChecked(False)
        elif sender == 'actionAlphabetical_order':
            self.ui.actionLast_check_in_order.setChecked(False)
        self.resetScreen()

    def remove_tribe_dialog(self):
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
                # Get list of all tribal locations
                tribes = self.db.list_all_tribal_locations()
                self.tribesList = []
                for tribe in tribes:
                    self.removeCombo.addItem(tribe[0])
                    self.tribesList.append(tribe[0])
                # Create button and connect it to removeTribe function
                btn = QPushButton('Ok')
                btn.pressed.connect(self.remove_tribe)
                # Cancel button
                cancel_btn = QPushButton('Cancel')
                cancel_btn.pressed.connect(self.removeDialog.close)
                # Add widgets to Grid and show dialog
                grid.addWidget(self.removeCombo, 0, 0, 0, 2)
                grid.addWidget(btn, 1, 0)
                grid.addWidget(cancel_btn, 1, 1)
                self.removeDialog.setLayout(grid)
                self.removeDialog.show()
        except Exception:
            logger.exception('removeTribe fail')

    def remove_tribe(self):
        logger.debug('removeTribe function called')
        # Called when Ok clicked in remove tribe dialog. Gets current tribe in combo
        # box and deletes it completely from .db
        try:
            tribe = self.tribesList[self.removeCombo.currentIndex()]
            self.db.delete_location(tribe)
            QMessageBox.about(self, 'Done', tribe + ' deleted from .db')
            self.removeDialog.close()
            self.resetScreen()
        except Exception:
            logger.exception('removeTribe fail')

    def add_tribe(self):
        logger.debug('addTribe function called')
        # called by a menu item, pulls up an input dialog to take the name of a
        # tribe to add to the .db
        try:
            new_tribe, ok = QInputDialog.getText(self, 'Add Tribe',
                                                'Enter name of new '
                                                'Tribal Location')
            if ok and new_tribe:
                # Create new .db row with family blank to be filled in later
                self.db.add_tribal_location(new_tribe, '')
                self.resetScreen()
        except Exception:
            logger.exception('addTribe fail')

    def edit_family_info(self):
        logger.debug('editFamilyInfo function called')
        # Called by the menu item, pulls up the family info for the selected tribe
        # which can be edited by the user
        try:
            # Get dialog layout ready
            self.editFamilyDialog = QDialog(w)
            self.editFamilyDialog.setWindowTitle('Edit family information')
            self.editFamilyDialog.resize(500, 800)
            editFamilyWidget = QWidget()
            scrollArea = QScrollArea()
            grid = QGridLayout()
            editGrid = QGridLayout()
            # Get active and inactive tribal locations
            text = self.db.list_all_tribal_locations()
            self.FEtribeLabels = []
            self.familyLineEdits = []
            # Fill a widget with labels and line edits
            for i, tribe in enumerate(text):
                lbl = QLabel(tribe[0])
                self.FEtribeLabels.append(lbl)
                line_edit = QLineEdit(tribe[1])
                line_edit.setMinimumWidth(300)
                self.familyLineEdits.append(line_edit)
                editGrid.addWidget(lbl, i, 0)
                editGrid.addWidget(line_edit, i, 1)
            # Create Ok button set to trigger updateFamilies function
            ok_btn = QPushButton('Ok')
            ok_btn.pressed.connect(self.update_families)
            # Place everything on a grid
            editGrid.addWidget(ok_btn, i + 1, 1)
            grid.addWidget(scrollArea)
            editFamilyWidget.setLayout(editGrid)
            self.editFamilyDialog.setLayout(grid)
            scrollArea.setWidget(editFamilyWidget)
            self.editFamilyDialog.show()
        except Exception:
            logger.exception('editFamilyInfo fail')

    def update_families(self):
        logger.debug('updateFamilies function called')
        # Called from editFamilyInfo function, closes dialog and updates .db
        for i, item in enumerate(self.familyLineEdits):
            self.db.update_family_info(item.text(), self.FEtribeLabels[i].text())
        self.editFamilyDialog.close()
        self.resetScreen()

    def undo_last(self):
        logger.debug('undoLast function called')
        # Called froma  menu item, finds last checkin, shows info in a message box
        # and asks for confirmation to delete from .db. Used to fix user misclicks
        try:
            checkin = self.db.get_last_user_action()
            checkinInfo = checkin[1] + ' who checked in by ' + checkin[2]
            msg = QMessageBox.question(w,
                                       'Delete last checkin',
                                       'The last checkin was: ' + checkinInfo +
                                       ' do you really want to delete this from .db?')
            if msg == QMessageBox.Yes:
                self.db.delete_last(checkin[0])
                self.resetScreen()
        except Exception:
            logger.exception('undoLast function fail')


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)


def main():
    global logger, w, app
    # Start logging
    logger = logSettings.create_logger(__name__)
    logger.addHandler(logging.StreamHandler())
    logger.info('GUI started')
    # Create GUI process
    app = QApplication(sys.argv)
    w = MyApp()
    w.show()
    # Check if .db exists or not. If not create it or load one before continuing
    # Should only execute on first use of program.
    if not os.path.exists('checkins.db'):
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
            EditDbDialog.CreateDBDialog(w).exec_()
        elif ret == 1:
            # Pull up a open file window if load called. Copy selected .db to
            # cwd, which should be the application folder
            logger.info('User chose to load existing .db')
            file = EditDbDialog.load_db(w)
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
        w.home(databaseFunc.DatabaseConnect())
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()