import logging

from PyQt5.QtWidgets import QDialog, QGridLayout, QPushButton, QPlainTextEdit

import function.logSettings as logSettings

logger = logSettings.create_logger(__name__)
logger.addHandler(logging.StreamHandler())


class InfoScreenWidget(QDialog):
    # Defines and pulls up a notepad type widget, the text of which is saved
    # to .db.
    def __init__(self, mw, db, tribe):
        try:
            QDialog.__init__(self, mw)
            self.db = db
            self.mw = mw
            self.tribe = tribe
            self.setWindowTitle('Info for ' + tribe)
            self.setGeometry(100, 150, 400, 350)
            self.setModal(True)
            self.grid = QGridLayout()
            self.textArea = QPlainTextEdit()
            self.currentInfo = self.db.get_info(tribe)
            self.textArea.appendPlainText(self.currentInfo)
            self.grid.addWidget(self.textArea, 0, 0)
            ok_btn = QPushButton('Ok')
            ok_btn.pressed.connect(self.save_info)
            self.grid.addWidget(ok_btn, 1, 0)
            self.setLayout(self.grid)
            self.show()
        except Exception:
            logger.exception('infoScreen fail')

    def save_info(self):
        logger.debug('Ok clicked on info widget')
        # Once Ok is clicked take text in widget and save to .db
        new_info = self.textArea.toPlainText()
        if self.currentInfo != new_info:  # Only save if changes made
            self.db.update_info(self.tribe, new_info)
            logger.info('new text saved to info')
        self.close()
