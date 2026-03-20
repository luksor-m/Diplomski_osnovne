from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMessageBox


from location_dialog import Ui_location_add_dialog
from location import Location

class Dialog_loc(QtWidgets.QDialog):

    def __init__(self):
        super(Dialog_loc, self).__init__()
        self.ui = Ui_location_add_dialog()
        self.ui.setupUi(self)

        self.setFixedSize(600, 344)
        self.ui.add_location_btn.clicked.connect(self.read_location)
        self.ui.cancel_location_btn.clicked.connect(self.close)

        self.location = None

    def read_location(self):

        name = self.ui.location_name_linedit.text()

        lat_dgr = self.ui.lat_dgr_linedit.text()
        lat_min = self.ui.lat_min_linedit.text()
        lat_sec = self.ui.lat_sec_linedit.text()

        long_dgr = self.ui.long_dgr_linedit.text()
        long_min = self.ui.long_min_linedit.text()
        long_sec = self.ui.long_sec_linedit.text()

        if len(name) == 0 or len(lat_dgr) == 0 or len(lat_min) == 0 or len(lat_sec) == 0 or len(long_dgr) == 0 or len(
                long_min) == 0 or len(long_sec) == 0:
            message = QMessageBox()
            message.setWindowTitle("GREŠKA!!!")
            message.setText("Neispravno unešeni podaci!")
            message.setStandardButtons(QMessageBox.StandardButton.Yes)

            yes_btn = message.button(QMessageBox.StandardButton.Yes)
            yes_btn.setText("U redu")

            message.exec()
        else:

            self.location = Location(name, lat_dgr, lat_min, lat_sec, long_dgr, long_min, long_sec)
            self.close()

