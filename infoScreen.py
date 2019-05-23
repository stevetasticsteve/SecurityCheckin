import logging
from PyQt5.QtWidgets import QDialog, QGridLayout, QPushButton, QPlainTextEdit 
import logSettings

logger = logSettings.createLogger(__name__)
logger.addHandler(logging.StreamHandler())

class infoScreenWidget(QDialog):
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
            self.currentInfo = self.db.getInfo(tribe)
            self.textArea.appendPlainText(self.currentInfo)
            self.grid.addWidget(self.textArea, 0, 0)
            okBtn = QPushButton('Ok')
            okBtn.pressed.connect(self.saveInfo)
            self.grid.addWidget(okBtn, 1, 0)
            self.setLayout(self.grid)
            self.show()
        except Exception:
            logger.exception('infoScreen fail')
            
            
    def saveInfo(self):
        logger.debug('Ok clicked on info widget')
        # Once Ok is clicked take text in widget and save to .db
        newInfo = self.textArea.toPlainText()
        if self.currentInfo != newInfo: # Only save if changes made
            self.db.updateInfo(self.tribe, newInfo)
            logger.info('new text saved to info')
        self.close()
        
