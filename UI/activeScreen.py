import logging
from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QPushButton, QCheckBox
import function.logSettings as logSettings

logger = logSettings.createLogger(__name__)
logger.addHandler(logging.StreamHandler())

class activeScreenWidget(QDialog):
    # defines a widget where user can tick check boxes to set active or inactive
    def __init__(self, mw, db):
        try:
            QDialog.__init__(self, mw)
            self.db = db
            self.mw = mw
            self.setWindowTitle('Set location as active or inactive')
            self.setGeometry(100, 150, 400, 350)
            self.setModal(True)
            self.grid = QGridLayout()

            activeTribes = self.db.listActiveTribalInfo()
            inactiveTribes  = self.db.listInactiveTribalInfo()
            self.allTribes = []
            self.checkBoxes = []

            # Add all active works to grid first with checkboxes ticked
            for i, tup in enumerate(activeTribes):
                tribeLbl = QLabel(tup[0])
                self.allTribes.append(tup[0])
                familyLbl = QLabel(tup[1])
                checkBox = QCheckBox()
                checkBox.setChecked(True)
                checkBox.setObjectName(tup[0])
                checkBox.toggled.connect(
                    lambda: self.changed(self.sender()))
                self.checkBoxes.append(checkBox)

                self.grid.addWidget(tribeLbl, i, 0)
                self.grid.addWidget(familyLbl, i, 1)
                self.grid.addWidget(checkBox, i, 2)

            # Prevents an IndexError if no tribes are inactive
            if activeTribes == []:
                i = 0
            i += 1

            # Then add all inactive with unticked checkboxes
            for j, tup in enumerate(inactiveTribes):
                tribeLbl = QLabel(tup[0])
                self.allTribes.append(tup[0])
                familyLbl = QLabel(tup[1])
                checkBox = QCheckBox()
                checkBox.setChecked(False)
                checkBox.setObjectName(tup[0])
                checkBox.toggled.connect(
                    lambda: self.changed(self.sender()))
                self.checkBoxes.append(checkBox)            

                self.grid.addWidget(tribeLbl, i + j, 0)
                self.grid.addWidget(familyLbl, i + j, 1)
                self.grid.addWidget(checkBox, i + j, 2)

            # Prevents and IndexError if all tribes are active
            if inactiveTribes == []:
                j = 0

            # Ok push button
            btn = QPushButton('Ok')
            btn.clicked.connect(self.close)
            self.grid.addWidget(btn, i + j + 1, 1)
            self.setLayout(self.grid)
            self.show()
        except Exception:
            logger.exception('Fail on active screen')

    def changed(self, tribe):
        logger.debug(tribe.objectName() + ' active/inactive changed')
        # Action whenever checkbox is changed
        try:
            if tribe.isChecked() == False:
                self.db.makeInactive(tribe.objectName())
            elif tribe.isChecked() == True:
                self.db.makeActive(tribe.objectName())
            self.mw.resetScreen()
        except Exception:
            logger.exception('Fail on active screen')

