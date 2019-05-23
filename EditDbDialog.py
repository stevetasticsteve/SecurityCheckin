import logging
import sys
from PyQt5.QtWidgets import QDialog, QLineEdit, QTableWidgetItem, QAbstractItemView
from PyQt5.QtWidgets import QGridLayout, QTableWidget, QPushButton
from PyQt5.QtWidgets import QMessageBox, QFileDialog
import logSettings 
import databaseFunc

logger = logSettings.createLogger(__name__)
logger.addHandler(logging.StreamHandler())

class createDBDialog(QDialog):
    def __init__(self,mw):
        QDialog.__init__(self,mw)
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
        
        addBtn = QPushButton(self)
        addBtn.setText('Add')
        addBtn.clicked.connect(self.addTribe)
        
        rmBtn = QPushButton(self)
        rmBtn.setText('Remove')
        rmBtn.clicked.connect(self.removeTribe)
        
        OkBtn = QPushButton(self)
        OkBtn.setText('OK')
        OkBtn.clicked.connect(self.closeDialog)
        
        self.grid.addWidget(self.tribesTbl, 0,0,5,5)
        self.grid.addWidget(addBtn, 6,1)
        self.grid.addWidget(self.lineInpt, 6,0)
        self.grid.addWidget(rmBtn, 4,6)
        self.grid.addWidget(OkBtn, 6,6)

        self.setLayout(self.grid)
        self.show()

    def errorHandling(self):
        logger.exception('Fatal Error:')
        QMessageBox.about(self, 'Error', 'A fatal error has occured, '
                      'check the log for details', )
        sys.exit()

    def addTribe(self):
        try:
            tribe = self.lineInpt.text()
            if tribe: #check not blank
                #add another if to check if already in table
                curRow = self.tribesTbl.rowCount()
                self.tribesTbl.setRowCount(curRow + 1)
                self.tribesTbl.setItem(curRow, 0 , QTableWidgetItem(tribe))
                self.lineInpt.setText('')
                self.lineInpt.setFocus()

        except Exception:
            self.errorHandling()

    def removeTribe(self):
        try:
            if self.tribesTbl.rowCount() > 0:
                curRow = self.tribesTbl.currentRow()
                if self.tribesTbl.item(curRow, 0):
                    if self.tribesTbl.item(curRow, 0).isSelected():
                        tribe = self.tribesTbl.currentItem().text()
                        print('removed ' + tribe)
                        self.tribesTbl.removeRow(self.tribesTbl.currentRow())
        except Exception:
            self.errorHandling()

    def readTable(self):
    # called as part of clicking Ok
        try:
            self.db = databaseFunc.databaseConnect()
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
                self.db.addTribalLocation(location, families[i])
            self.db.closeDatabase()
        except Exception:
            self.errorHandling()           
            

    def closeDialog(self):
    # function called when OK is clicked
        try:
            if self.tribesTbl.rowCount() > 0:
            #only allow .db creation with at least 1 tribe
                self.readTable()
                self.close()
                return self.db
            else:
                pass
        except Exception:
            self.errorHandling()
                        

def loadDB(self):
    #Called by hitting load when no .db exists.
    logger.debug('Load called')
    try:
        file, _ = QFileDialog.getOpenFileName(self, 'Select db', "" , 'Database (*.db)')
        if file:
            return file
        else:
            return None
    except Exception:
        logger.exception('Load fail')
