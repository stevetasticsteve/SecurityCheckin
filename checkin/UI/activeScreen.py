import logging

from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QPushButton, QCheckBox

import checkin.function.logSettings as logSettings

logger = logSettings.create_logger(__name__)
logger.addHandler(logging.StreamHandler())


class Activescreenwidget(QDialog):
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

            active_tribes = self.db.list_active_tribal_info()
            inactive_tribes = self.db.list_inactive_tribal_info()
            self.allTribes = []
            self.checkBoxes = []

            # Add all active works to grid first with checkboxes ticked
            for i, tup in enumerate(active_tribes):
                tribe_lbl = QLabel(tup[0])
                self.allTribes.append(tup[0])
                family_lbl = QLabel(tup[1])
                check_box = QCheckBox()
                check_box.setChecked(True)
                check_box.setObjectName(tup[0])
                check_box.toggled.connect(
                    lambda: self.changed(self.sender()))
                self.checkBoxes.append(check_box)

                self.grid.addWidget(tribe_lbl, i, 0)
                self.grid.addWidget(family_lbl, i, 1)
                self.grid.addWidget(check_box, i, 2)

            # Prevents an IndexError if no tribes are inactive
            if not active_tribes:
                i = 0
            i += 1

            # Then add all inactive with unticked checkboxes
            for j, tup in enumerate(inactive_tribes):
                tribe_lbl = QLabel(tup[0])
                self.allTribes.append(tup[0])
                family_lbl = QLabel(tup[1])
                check_box = QCheckBox()
                check_box.setChecked(False)
                check_box.setObjectName(tup[0])
                check_box.toggled.connect(
                    lambda: self.changed(self.sender()))
                self.checkBoxes.append(check_box)

                self.grid.addWidget(tribe_lbl, i + j, 0)
                self.grid.addWidget(family_lbl, i + j, 1)
                self.grid.addWidget(check_box, i + j, 2)

            # Prevents and IndexError if all tribes are active
            if not inactive_tribes:
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
            if not tribe.isChecked():
                self.db.make_inactive(tribe.objectName())
            elif tribe.isChecked():
                self.db.makeActive(tribe.objectName())
            self.mw.resetScreen()
        except Exception:
            logger.exception('Fail on active screen')
