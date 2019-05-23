import logging
from PyQt5.QtWidgets import QDialog, QCalendarWidget, QGridLayout
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QDate
import logSettings

logger = logSettings.createLogger(__name__)
logger.addHandler(logging.StreamHandler())

class calendarWidget(QDialog):
    def __init__(self, mw, tribe, db):
        try:
            QDialog.__init__(self, mw)
            self.setWindowTitle('Check in history for ' + tribe)
            self.setGeometry(100, 150, 900, 550)
            self.setModal(True)
            self.grid = QGridLayout()
            self.cal = calendar()
            # get checkin info
            self.cal.checkins = QDate(2019,1,1)
            self.fillCal(db, tribe)
            self.grid.addWidget(self.cal,0,0)
            self.setLayout(self.grid)
            self.show()
        except Exception:
            logger.exception('calendarWidget error')
            
    def fillCal(self,db, tribe):
        try:
            data = db.listCheckinHistory(tribe)
            self.cal.checkins = []
            self.cal.methods = []
            for item in data:
                self.cal.checkins.append(item[0].date())
                self.cal.methods.append(item[1])
        except Exception:
            logger.exception('error filling calendar')

# a modified QCalendarWidget class with the paintCell function re-coded.
# This allows days to be drawn in with checkin info
class calendar(QCalendarWidget):
    def paintCell(self, painter, rect, date):
            if date in self.checkins:
                colour = QColor(255, 0, 0, 50)
                painter.fillRect(rect, colour)
                painter.drawText(rect.center(), str(date.day()))
                painter.drawText(rect.bottomLeft(),
                                 self.methods[self.checkins.index(date)])
            else:
                QCalendarWidget.paintCell(self,painter,rect,date)
