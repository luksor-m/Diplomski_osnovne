from PyQt6 import QtWidgets
from PyQt6.QtWidgets import  QMessageBox


from link_dialog import Ui_link_add_dialog

class Dialog_link(QtWidgets.QDialog):
    antennas_name_gain = []

    def __init__(self):
        super(Dialog_link, self).__init__()
        self.ui = Ui_link_add_dialog()
        self.ui.setupUi(self)

        self.setFixedSize(548, 416)
        self.ui.add_link_btn.clicked.connect(self.read_link)
        self.ui.cancel_link_btn.clicked.connect(self.close)


        self.ui.ant1_model_combo.currentIndexChanged.connect(self.__change_ant1_gain)
        self.ui.ant2_model_combo.currentIndexChanged.connect(self.__change_ant2_gain)

        self.link = None

    def read_link(self):
        name = self.ui.link_name_linedit.text()
        loc_1 = self.ui.location1_combo.currentText()
        loc_2 = self.ui.location2_combo.currentText()

        ant1_name = self.ui.ant1_model_combo.currentText()
        ant1_pwr = self.ui.ant1_pwr_linedit.text()
        ant1_loss = self.ui.ant1_los_linedit.text()
        ant1_gain = self.ui.ant1_gain_linedit.text()

        ant2_name = self.ui.ant2_model_combo.currentText()
        ant2_pwr = self.ui.ant2_pwr_linedit.text()
        ant2_loss = self.ui.ant2_los_linedit.text()
        ant2_gain = self.ui.ant2_gain_linedit.text()

        if len(name) == 0 or len(loc_1) == 0 or len(loc_2) == 0 or \
                len(ant1_name) == 0 or len(ant1_pwr) == 0 or \
                len(ant1_loss) == 0 or len(ant1_gain) == 0 or \
                len(ant2_name) == 0 or len(ant2_pwr) == 0 or \
                len(ant2_loss) == 0 or len(ant2_gain) == 0:

            message = QMessageBox()
            message.setWindowTitle("GREŠKA!!!")
            message.setText("Neispravno unešeni podaci!")
            message.setStandardButtons(QMessageBox.StandardButton.Yes)

            yes_btn = message.button(QMessageBox.StandardButton.Yes)
            yes_btn.setText("U redu")

            message.exec()
        elif loc_1 == loc_2:
            message = QMessageBox()
            message.setWindowTitle("GREŠKA!!!")
            message.setText("Unešena ista lokacija!")
            message.setStandardButtons(QMessageBox.StandardButton.Yes)

            yes_btn = message.button(QMessageBox.StandardButton.Yes)
            yes_btn.setText("U redu")

            message.exec()

        else:
            self.link = [name, loc_1, ant1_name,  ant1_pwr, ant1_loss, ant1_gain, loc_2, ant2_name,
                         ant2_pwr, ant2_loss, ant2_gain]
            self.close()

    def __change_ant1_gain(self):
        if self.ui.ant1_model_combo.currentText() == "":
            self.ui.ant1_gain_linedit.setText("")
        else:
            model = self.ui.ant1_model_combo.currentText()
            for ant in self.antennas_name_gain:
                if model == ant[0]:
                    self.ui.ant1_gain_linedit.setText(ant[1])

    def __change_ant2_gain(self):
        if self.ui.ant2_model_combo.currentText() == "":
            self.ui.ant2_gain_linedit.setText("")
        else:
            model = self.ui.ant2_model_combo.currentText()
            for ant in self.antennas_name_gain:
                if model == ant[0]:
                    self.ui.ant2_gain_linedit.setText(ant[1])
