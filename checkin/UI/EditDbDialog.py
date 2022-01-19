import logging
import sys

from PyQt5.QtWidgets import QDialog, QLineEdit, QTableWidgetItem, QAbstractItemView
from PyQt5.QtWidgets import QGridLayout, QTableWidget, QPushButton
from PyQt5.QtWidgets import QMessageBox, QFileDialog

import checkin.function.databaseFunc as databaseFunc
import checkin.function.logSettings  as logSettings

logger = logSettings.create_logger(__name__)
logger.addHandler(logging.StreamHandler())


class CreateDBDialog(QDialog):
    def __init__(self, mw):
        QDialog.__init__(self, mw)
        self.setWindowTitle('Create database')
        self.setGeometry(100, 150, 900, 550)
        self.setModal(True)
        self.grid = QGridLayout()
        self.grid.setSpacing(10)

        self.tribesTbl = QTableWidget(self)
        self.tribesTbl.setColumnCount(2)
        self.tribesTbl.setRowCount(0)
        self.tribesTbl.setHorizontalHeaderLabels(['Tribe', 'Families'])
        self.tribesTbl.setSelectionMode(QAbstractItemView.SingleSelection)
        self.lineInpt = QLineEdit(self)
        self.lineInpt.setFocus()

        add_btn = QPushButton(self)
        add_btn.setText('Add')
        add_btn.clicked.connect(self.add_tribe)

        rm_btn = QPushButton(self)
        rm_btn.setText('Remove')
        rm_btn.clicked.connect(self.remove_tribe)

        ok_btn = QPushButton(self)
        ok_btn.setText('OK')
        ok_btn.clicked.connect(self.close_dialog)

        self.grid.addWidget(self.tribesTbl, 0, 0, 5, 5)
        self.grid.addWidget(add_btn, 6, 1)
        self.grid.addWidget(self.lineInpt, 6, 0)
        self.grid.addWidget(rm_btn, 4, 6)
        self.grid.addWidget(ok_btn, 6, 6)

        self.setLayout(self.grid)
        self.show()

    def error_handling(self):
        logger.exception('Fatal Error:')
        QMessageBox.about(self, 'Error', 'A fatal error has occured, '
                                         'check the log for details', )
        sys.exit()

    def add_tribe(self):
        try:
            tribe = self.lineInpt.text()
            if tribe:  # check not blank
                # add another if to check if already in table
                cur_row = self.tribesTbl.rowCount()
                self.tribesTbl.setRowCount(cur_row + 1)
                self.tribesTbl.setItem(cur_row, 0, QTableWidgetItem(tribe))
                self.lineInpt.setText('')
                self.lineInpt.setFocus()

        except Exception:
            self.error_handling()

    def remove_tribe(self):
        try:
            if self.tribesTbl.rowCount() > 0:
                curRow = self.tribesTbl.currentRow()
                if self.tribesTbl.item(curRow, 0):
                    if self.tribesTbl.item(curRow, 0).isSelected():
                        tribe = self.tribesTbl.currentItem().text()
                        print('removed ' + tribe)
                        self.tribesTbl.removeRow(self.tribesTbl.currentRow())
        except Exception:
            self.error_handling()

    def read_table(self):
        # called as part of clicking Ok
        try:
            self.db = databaseFunc.DatabaseConnect()
            tribes = []
            families = []
            for row in range(self.tribesTbl.rowCount()):
                tribe = self.tribesTbl.item(row, 0).text()
                tribes.append(tribe)
                if self.tribesTbl.item(row, 1):
                    family = self.tribesTbl.item(row, 1).text()
                else:
                    family = 'info not entered'
                families.append(family)
            for i, location in enumerate(tribes):
                self.db.add_tribal_location(location, families[i])
            self.db.close_database()
        except Exception:
            self.error_handling()

    def close_dialog(self):
        # function called when OK is clicked
        try:
            if self.tribesTbl.rowCount() > 0:
                # only allow .db creation with at least 1 tribe
                self.read_table()
                self.close()
                return self.db
            else:
                pass
        except Exception:
            self.error_handling()


def load_db(self):
    # Called by hitting load when no .db exists.
    logger.debug('Load called')
    try:
        file, _ = QFileDialog.getOpenFileName(self, 'Select db', "", 'Database (*.db)')
        if file:
            return file
        else:
            return None
    except Exception:
        logger.exception('Load fail')
