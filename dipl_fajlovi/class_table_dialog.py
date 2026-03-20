from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QInputDialog, QLineEdit, QMessageBox, QListWidget, QListWidgetItem, QFileDialog

import sys
import pandas as pd

from table_dialog import Ui_Dialog

class Dialog_table(QtWidgets.QDialog):

    def __init__(self):
        super(Dialog_table, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.setFixedSize(594, 525)
        self.ui.go_back_btn.clicked.connect(self.close)
        self.ui.save_data_btn.clicked.connect(self.exportToExcel)


    def exportToExcel(self):
        # Open a file dialog to choose the save location and file name
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", "",
                                                   "Excel Files (*.xlsx);;All Files (*)")

        if file_path:

            rows = self.ui.interference_table.rowCount()
            columns = self.ui.interference_table.columnCount()
            table_data = []

            for row in range(rows):
                row_data = []
                for column in range(columns):
                    item = self.ui.interference_table.item(row, column)
                    row_data.append(item.text() if item else "")
                table_data.append(row_data)

            df = pd.DataFrame(table_data)

            df.to_excel(file_path, index=False, header=False)
