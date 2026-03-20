from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QInputDialog, QLineEdit, QMessageBox, QListWidget, QListWidgetItem, QFileDialog, \
QApplication, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, QTableWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QPixmap, QBrush


from dipl_diz import Ui_MainWindow
from class_loc_dialog import Dialog_loc
from class_link_dialog import Dialog_link
from class_table_dialog import Dialog_table
from graphich_items import *
from class_map_view import map_view

from location import Location
from link import Link
from antenna import Antenna
import sys
import os
import shutil
import math
from pathlib import Path
from typing import List
from collections import deque
import json

class window(QtWidgets.QMainWindow):
    def __init__(self):
        super(window, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setFixedSize(self.width(), self.height())
        self.ui.add_location_btn.clicked.connect(self.add_location)
        self.ui.modify_location_btn.clicked.connect(self.modify_location)
        self.ui.remove_location_btn.clicked.connect(self.remove_location)

        self.ui.add_link_btn.clicked.connect(self.add_link)
        self.ui.modify_link_btn.clicked.connect(self.modify_link)
        self.ui.remove_link_btn.clicked.connect(self.remove_link)
        self.ui.calc_a_and_b_btn.clicked.connect(self.__calc_a_and_b_st)

        self.ui.loc1_combo.currentTextChanged.connect(self.__change_ant1_color)
        self.ui.loc2_combo.currentTextChanged.connect(self.__change_ant2_color)

        self.ui.calculate_btn.clicked.connect(self.__view_data_table)

        self.ui.load_antenna_btn.clicked.connect(self.add_new_antenna)

        self.ui.actionSa_uvaj_fajl.triggered.connect(self.save_as)
        self.ui.actionSa_uvaj.triggered.connect(self.save)
        self.ui.actionOtvori_fajl.triggered.connect(self.load)
        self.ui.actionNovi_projekat.triggered.connect(self.new)

        self.__a_b_flag = None

        self.locations: List[Location] = []
        self.links: List[Link] = []
        self.antennas = []

        self.__paint_on_map()
        if len(self.antennas) == 0:
            self.__load_antennas()

        self.current_file = None

    def new(self):

        question = QMessageBox()
        question.setWindowTitle("Uklanjanje lokacije")
        question.setText("Da li ste sigurni da želite da otvorite novi projekat?")
        question.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        yes_btn = question.button(QMessageBox.StandardButton.Yes)
        yes_btn.setText("Nastavi")

        no_btn = question.button(QMessageBox.StandardButton.No)
        no_btn.setText("Otkaži")

        reply = question.exec()

        if reply == QMessageBox.StandardButton.Yes:
            question = QMessageBox()
            question.setWindowTitle("Uklanjanje lokacije")
            question.setText("Želite li da sačuvate tekući projekat?")
            question.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            yes_btn = question.button(QMessageBox.StandardButton.Yes)
            yes_btn.setText("Sačuvaj")

            no_btn = question.button(QMessageBox.StandardButton.No)
            no_btn.setText("Otkaži")

            reply = question.exec()

            if reply == QMessageBox.StandardButton.Yes:
                self.save()

            self.ui.list_of_locations.clear()
            self.ui.list_of_links.clear()
            self.ui.loc1_combo.clear()
            self.ui.loc2_combo.clear()
            self.ui.freq_linedit.setText("")

            self.locations: List[Location] = []
            self.links: List[Link] = []
            self.antennas = []
            self.__load_antennas()

            self.__a_b_flag = None
            self.current_file = None

            for button in self.ui.buttonGroup.buttons():
                if button.isChecked():
                    button.setAutoExclusive(False)
                    button.setChecked(False)
                    button.setAutoExclusive(True)
                    button.setCheckable(False)
                    button.update()
                    button.setCheckable(True)

            for button in self.ui.buttonGroup_2.buttons():
                if button.isChecked():
                    button.setAutoExclusive(False)
                    button.setChecked(False)
                    button.setAutoExclusive(True)
                    button.setCheckable(False)
                    button.update()
                    button.setCheckable(True)

            for button in self.ui.buttonGroup_3.buttons():
                if button.isChecked():
                    button.setAutoExclusive(False)
                    button.setChecked(False)
                    button.setAutoExclusive(True)
                    button.setCheckable(False)
                    button.update()
                    button.setCheckable(True)

            self.__paint_on_map()

    def save_as(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Sačuvaj kao", "", "JSON Files (*.json);;All Files (*)")
        if file_name:
            self.current_file = file_name
            self.save()

    def save(self):
        if not self.current_file:
            self.save_as()
        else:
            state = {
                'window_geometry': self.saveGeometry().data().hex(),
                'window_state': self.saveState().data().hex(),

                'locations_list_items': [self.ui.list_of_locations.item(i).text() for i in
                                         range(self.ui.list_of_locations.count())],
                'links_list_items': [self.ui.list_of_links.item(i).text() for i in
                                     range(self.ui.list_of_links.count())],
                'combo_box1_items': [self.ui.loc1_combo.itemText(i) for i in range(self.ui.loc1_combo.count())],
                'combo_box2_items': [self.ui.loc2_combo.itemText(i) for i in range(self.ui.loc2_combo.count())],
                'line_edit_text': self.ui.freq_linedit.text(),

                'a_b_flag': self.__a_b_flag,
                'locations': [location.to_dict() for location in self.locations],
                'links': [link.to_dict() for link in self.links],
                'antennas': self.antennas  # Directly save the list
            }
            try:
                with open(self.current_file, 'w') as file:
                    json.dump(state, file, indent=4)
                QMessageBox.information(self, "Sačuvaj", "Fajl uspešno sačuvan!")
            except Exception as e:
                QMessageBox.critical(self, "Sačuvaj", f"Greška pri čuvanju fajla: {e}")

    def load(self):

        file_name, _ = QFileDialog.getOpenFileName(self, "Load", "", "JSON Files (*.json);;All Files (*)")
        if file_name:
            try:
                with open(file_name, 'r') as file:
                    state = json.load(file)
                    self.restoreGeometry(bytes.fromhex(state['window_geometry']))
                    self.restoreState(bytes.fromhex(state['window_state']))

                    self.ui.list_of_locations.clear()
                    self.ui.list_of_locations.addItems(state['locations_list_items'])

                    self.ui.list_of_links.clear()
                    self.ui.list_of_links.addItems(state['links_list_items'])

                    self.ui.loc1_combo.clear()
                    self.ui.loc1_combo.addItems(state['combo_box1_items'])

                    self.ui.loc2_combo.clear()
                    self.ui.loc2_combo.addItems(state['combo_box2_items'])

                    self.ui.freq_linedit.setText(state['line_edit_text'])

                    self.locations = [Location.from_dict(item) for item in state.get('locations', [])]
                    self.links = [Link.from_dict(item) for item in state.get('links', [])]

                    help_list = state.get('antennas', [])
                    unique = [antenna for antenna in help_list if antenna not in self.antennas]
                    for antenna in unique:
                        self.antennas.append(antenna)


                    self.current_file = file_name

                    self.__a_b_flag = state['a_b_flag']

                    for button in self.ui.buttonGroup.buttons():
                        if button.isChecked():
                            button.setAutoExclusive(False)
                            button.setChecked(False)
                            button.setAutoExclusive(True)
                            button.setCheckable(False)
                            button.update()
                            button.setCheckable(True)

                    for button in self.ui.buttonGroup_2.buttons():
                        if button.isChecked():
                            button.setAutoExclusive(False)
                            button.setChecked(False)
                            button.setAutoExclusive(True)
                            button.setCheckable(False)
                            button.update()
                            button.setCheckable(True)

                    for button in self.ui.buttonGroup_3.buttons():
                        if button.isChecked():
                            button.setAutoExclusive(False)
                            button.setChecked(False)
                            button.setAutoExclusive(True)
                            button.setCheckable(False)
                            button.update()
                            button.setCheckable(True)


                    self.__paint_on_map()

                    QMessageBox.information(self, "Učitaj", "Fajl uspešno učitan!")

            except Exception as e:
                QMessageBox.critical(self, "Učitaj", f"Greška pri učitavanju: {e}")

    def __load_antennas(self):
        path = Path(os.getcwd() + "/Antene")
        files = [file.name for file in path.iterdir() if file.is_file()]
        for i in range(0, len(files)):
            files[i] = files[i][0:-4]
            gain, HH, HV, VV, VH = self.__read_ant_file(files[i])
            var = [files[i], gain, HH, HV, VV, VH]
            self.antennas.append(var)

    def __update_antennas(self, antenna):

        gain, HH, HV, VV, VH = self.__read_ant_file(antenna)
        var = [antenna, gain, HH, HV, VV, VH]
        self.antennas.append(var)

    def add_new_antenna(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Izaberi antenu', '', 'All Files (*)')
        folder_path = os.getcwd() + "\Antene"
        parts = file_path.rsplit('/', 1)
        if file_path:
            destination_path = os.path.join(folder_path, os.path.basename(file_path))
            shutil.copy(file_path, destination_path)
            self.__update_antennas(parts[1][0:-4])
        else:
            message = QMessageBox()
            message.setWindowTitle("GREŠKA!!!")
            message.setText("Nije izabran fajl!")
            message.setStandardButtons(QMessageBox.StandardButton.Yes)
            yes_btn = message.button(QMessageBox.StandardButton.Yes)
            yes_btn.setText("U redu")

            message.exec()
            return

    def add_link(self):

        if len(self.locations) < 2:
            message = QMessageBox()
            message.setWindowTitle("GREŠKA!!!")
            message.setText("Ne može se formirati link broj lokacija manji od 2!")
            message.setStandardButtons(QMessageBox.StandardButton.Yes)

            yes_btn = message.button(QMessageBox.StandardButton.Yes)
            yes_btn.setText("U redu")

            message.exec()
        else:
            dialog = Dialog_link()

            dialog.ui.ant1_model_combo.addItem("")
            dialog.ui.ant1_model_combo.setCurrentIndex(0)

            dialog.ui.ant2_model_combo.addItem("")
            dialog.ui.ant2_model_combo.setCurrentIndex(0)

            for i in range(0, len(self.locations)):
                dialog.ui.location1_combo.addItem(self.locations[i].get_name())
                dialog.ui.location2_combo.addItem(self.locations[i].get_name())
            for i in range(0, len(self.antennas)):
                dialog.ui.ant1_model_combo.addItem(self.antennas[i][0])
                dialog.ui.ant2_model_combo.addItem(self.antennas[i][0])
                dialog.antennas_name_gain.append([self.antennas[i][0], self.antennas[i][1]])

            dialog.exec()

            if dialog.link is not None:
                loc_1_ind = None
                loc_2_ind = None

                for i in range(0, len(self.locations)):
                    if self.locations[i].get_name() == dialog.link[1]:
                        loc_1_ind = i
                        break

                for i in range(0, len(self.locations)):
                    if self.locations[i].get_name() == dialog.link[6]:
                        loc_2_ind = i
                        break


                loc1 = self.locations[loc_1_ind]
                loc2 = self.locations[loc_2_ind]

                ant1 = Antenna(dialog.link[2], dialog.link[3], dialog.link[4], dialog.link[5])
                ant2 = Antenna(dialog.link[7], dialog.link[8], dialog.link[9], dialog.link[10])

                for i in range(len(self.antennas)):
                    if ant1.get_name() == self.antennas[i][0]:
                        ant1.set_HH(self.antennas[i][2])
                        ant1.set_HV(self.antennas[i][3])
                        ant1.set_VV(self.antennas[i][4])
                        ant1.set_VH(self.antennas[i][5])

                for i in range(len(self.antennas)):
                    if ant2.get_name() == self.antennas[i][0]:
                        ant2.set_HH(self.antennas[i][2])
                        ant2.set_HV(self.antennas[i][3])
                        ant2.set_VV(self.antennas[i][4])
                        ant2.set_VH(self.antennas[i][5])

                link = Link(dialog.link[0], loc1, ant1, loc2, ant2)


                if link != None:
                    link_item = QListWidgetItem(str(link))
                    link_item.setData(257, link)
                    self.ui.list_of_links.addItem(link_item)
                    self.links.append(link)
                    self.__a_b_flag = False
                    self.__reset_ant_colors()
                    self.__reset_loc_colors()
                    self.__paint_on_map()
                    self.__add_antennas_to_combos()


    def modify_link(self):
        index = self.ui.list_of_links.currentRow()
        link_item = self.ui.list_of_links.item(index)

        if link_item is None:
            return

        dialog = Dialog_link()

        dialog.ui.ant1_model_combo.addItem("")
        dialog.ui.ant2_model_combo.addItem("")

        for i in range(0, len(self.locations)):
            dialog.ui.location1_combo.addItem(self.locations[i].get_name())
            dialog.ui.location2_combo.addItem(self.locations[i].get_name())

        for i in range(0, len(self.antennas)):
            dialog.ui.ant1_model_combo.addItem(self.antennas[i][0])
            dialog.ui.ant2_model_combo.addItem(self.antennas[i][0])
            dialog.antennas_name_gain.append([self.antennas[i][0], self.antennas[i][1]])

        dialog.ui.link_name_linedit.setText(self.links[index].get_name())

        dialog.ui.ant1_pwr_linedit.setText(self.links[index].get_antenna1().get_pwr())
        dialog.ui.ant1_los_linedit.setText(self.links[index].get_antenna1().get_loss())
        dialog.ui.ant1_gain_linedit.setText(self.links[index].get_antenna1().get_gain())

        dialog.ui.ant2_pwr_linedit.setText(self.links[index].get_antenna2().get_pwr())
        dialog.ui.ant2_los_linedit.setText(self.links[index].get_antenna2().get_loss())
        dialog.ui.ant2_gain_linedit.setText(self.links[index].get_antenna2().get_gain())

        index_loc1 = dialog.ui.location1_combo.findText(self.links[index].get_location1().get_name())
        dialog.ui.location1_combo.setCurrentIndex(index_loc1)

        index_ant1 = dialog.ui.ant1_model_combo.findText(self.links[index].get_antenna1().get_name())
        dialog.ui.ant1_model_combo.setCurrentIndex(index_ant1)

        index_loc2 = dialog.ui.location2_combo.findText(self.links[index].get_location2().get_name())
        dialog.ui.location2_combo.setCurrentIndex(index_loc2)

        index_ant2 = dialog.ui.ant2_model_combo.findText(self.links[index].get_antenna2().get_name())
        dialog.ui.ant2_model_combo.setCurrentIndex(index_ant2)

        dialog.ui.add_link_btn.setText("Izmeni link")
        dialog.ui.cancel_link_btn.setText("Otkaži izmenu")
        dialog.exec()

        if dialog.link is not None:
            loc_1_ind = None
            loc_2_ind = None

            for i in range(0, len(self.locations)):
                if self.locations[i].get_name() == dialog.link[1]:
                    loc_1_ind = i
                    break

            for i in range(0, len(self.locations)):
                if self.locations[i].get_name() == dialog.link[6]:
                    loc_2_ind = i
                    break



            loc1 = self.locations[loc_1_ind]
            loc2 = self.locations[loc_2_ind]

            ant1 = Antenna(dialog.link[2], dialog.link[3], dialog.link[4], dialog.link[5])
            ant2 = Antenna(dialog.link[7], dialog.link[8], dialog.link[9], dialog.link[10])

            for i in range(len(self.antennas)):
                if ant1.get_name() == self.antennas[i][0]:
                    ant1.set_HH(self.antennas[i][2])
                    ant1.set_HV(self.antennas[i][3])
                    ant1.set_VV(self.antennas[i][4])
                    ant1.set_VH(self.antennas[i][5])

            for i in range(len(self.antennas)):
                if ant2.get_name() == self.antennas[i][0]:
                    ant2.set_HH(self.antennas[i][2])
                    ant2.set_HV(self.antennas[i][3])
                    ant2.set_VV(self.antennas[i][4])
                    ant2.set_VH(self.antennas[i][5])

            new_link = Link(dialog.link[0], loc1, ant1, loc2, ant2)

            if new_link != None:
                link_item.setText(str(new_link))
                link_item.setData(257, new_link)
                self.links.insert(index, new_link)
                self.links.pop(index + 1)
                self.__a_b_flag = False
                self.__reset_ant_colors()
                self.__reset_loc_colors()
                self.__paint_on_map()
                self.__add_antennas_to_combos()

    def remove_link(self):
        index = self.ui.list_of_links.currentRow()
        item = self.ui.list_of_links.item(index)
        if item is None:
            return

        question = QMessageBox()
        question.setWindowTitle("Uklanjanje linka")
        question.setText("Da li ste sigurni da želite da uklonite link " + item.text() + "?")
        question.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        yes_btn = question.button(QMessageBox.StandardButton.Yes)
        yes_btn.setText("Ukloni")

        no_btn = question.button(QMessageBox.StandardButton.No)
        no_btn.setText("Otkaži")

        reply = question.exec()

        if reply == QMessageBox.StandardButton.Yes:
            self.ui.list_of_links.takeItem(index)
            self.links.pop(index)
            del item
            self.__a_b_flag = False
            self.__reset_ant_colors()
            self.__reset_loc_colors()
            self.__paint_on_map()
            self.__add_antennas_to_combos()

    def add_location(self):
        dialog = Dialog_loc()
        dialog.exec()

        location = dialog.location

        if location != None:
            location_item = QListWidgetItem(str(location))
            location_item.setData(256, location)
            self.ui.list_of_locations.addItem(location_item)
            self.locations.append(location)
            self.__paint_on_map()

    def modify_location(self):

        index = self.ui.list_of_locations.currentRow()
        location_item = self.ui.list_of_locations.item(index)

        if location_item is None:
            return

        part_of_existing_link = False

        for i in range(0, len(self.links)):
            if self.links[i].get_location1().get_name() == self.locations[index].get_name() or self.links[
                i].get_location2().get_name() == \
                    self.locations[index].get_name():
                part_of_existing_link = True

        if part_of_existing_link:
            message = QMessageBox()
            message.setWindowTitle("GREŠKA!!!")
            message.setText("Lokacija se ne može menjati jer pripada postojećem linku!")
            message.setStandardButtons(QMessageBox.StandardButton.Yes)
            yes_btn = message.button(QMessageBox.StandardButton.Yes)
            yes_btn.setText("U redu")

            message.exec()
            return

        dialog = Dialog_loc()

        dialog.ui.location_name_linedit.setText(self.locations[index].get_name())
        dialog.ui.lat_dgr_linedit.setText(self.locations[index].get_latitude_dgr())
        dialog.ui.lat_min_linedit.setText(self.locations[index].get_latitude_min())
        dialog.ui.lat_sec_linedit.setText(self.locations[index].get_latitude_sec())
        dialog.ui.long_dgr_linedit.setText(self.locations[index].get_longitude_dgr())
        dialog.ui.long_min_linedit.setText(self.locations[index].get_longitude_min())
        dialog.ui.long_sec_linedit.setText(self.locations[index].get_longitude_sec())
        dialog.ui.add_location_btn.setText("Izmeni lokaciju")
        dialog.ui.cancel_location_btn.setText("Otkaži izmenu")

        dialog.exec()

        new_location = dialog.location

        if new_location != None:
            location_item.setText(str(new_location))
            location_item.setData(256, new_location)
            self.locations.insert(index, new_location)
            self.locations.pop(index + 1)
            self.__paint_on_map()


    def remove_location(self):

        index = self.ui.list_of_locations.currentRow()
        item = self.ui.list_of_locations.item(index)
        if item is None:
            return

        part_of_existing_link = False

        for i in range(0, len(self.links)):
            if self.links[i].get_location1().get_name() == self.locations[index].get_name() or self.links[
                i].get_location2().get_name() == self.locations[index].get_name():
                part_of_existing_link = True

        if part_of_existing_link:
            message = QMessageBox()
            message.setWindowTitle("GREŠKA!!!")
            message.setText("Lokacija se ne može ukloniti jer pripada postojećem linku!")
            message.setStandardButtons(QMessageBox.StandardButton.Yes)
            yes_btn = message.button(QMessageBox.StandardButton.Yes)
            yes_btn.setText("U redu")

            message.exec()
            return

        else:
            question = QMessageBox()
            question.setWindowTitle("Uklanjanje lokacije")
            question.setText("Da li ste sigurni da želite da uklonite lokaciju " + item.text() + "?")
            question.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            yes_btn = question.button(QMessageBox.StandardButton.Yes)
            yes_btn.setText("Ukloni")

            no_btn = question.button(QMessageBox.StandardButton.No)
            no_btn.setText("Otkaži")

            reply = question.exec()

            if reply == QMessageBox.StandardButton.Yes:
                self.ui.list_of_locations.takeItem(index)
                self.locations.pop(index)
                del item
                self.__paint_on_map()


    def __paint_on_map(self):
        hei = self.ui.map_gview.height()
        widt = self.ui.map_gview.width()
        self.ui.map_gview.scene = QGraphicsScene(0, 0, widt, hei)
        self.ui.map_gview.setScene(self.ui.map_gview.scene)
        self.ui.map_gview.setBackgroundBrush(Qt.GlobalColor.lightGray)

        for link in self.links:
            link_item = MapItemLink(link.get_location1().get_x_paint(),hei -link.get_location1().get_y_paint(),
                                    link.get_location2().get_x_paint(),hei -link.get_location2().get_y_paint())
            self.ui.map_gview.scene.addItem(link_item)

            ant1_x1, ant1_y1, ant1_x2, ant1_y2, ant2_x1, \
            ant2_y1, ant2_x2, ant2_y2 = self.__calc_antennas_paint_cod(link.get_location1().get_x_paint(),
                                                                       hei - link.get_location1().get_y_paint(),
                                                                       link.get_location2().get_x_paint(),
                                                                       hei - link.get_location2().get_y_paint())

            ant1_item = MapItemAntena(ant1_x1, ant1_y1, ant1_x2, ant1_y2, link.get_antenna1().get_color())
            ant2_item = MapItemAntena(ant2_x1, ant2_y1, ant2_x2, ant2_y2, link.get_antenna2().get_color())

            self.ui.map_gview.scene.addItem(ant1_item)
            self.ui.map_gview.scene.addItem(ant2_item)

        for loc in self.locations:
            loc_item = MapItemLocation(loc.get_x_paint(),hei - loc.get_y_paint(), 5, loc.get_color())
            text_item = MapItemText(loc.get_x_paint()+3 , hei - loc.get_y_paint() , loc.get_name())
            self.ui.map_gview.scene.addItem(loc_item)
            self.ui.map_gview.scene.addItem(text_item)

        self.ui.map_gview.show()



    def __calc_a_and_b_st(self):

        neighbors_list = self.__form_network_tree()
        if self.__has_odd_cycle(neighbors_list) is True:
            message = QMessageBox()
            message.setWindowTitle("GREŠKA!!!")
            message.setText("Postoji zatvorena petlja sa neparnim brojem linkova!!!!")
            message.setStandardButtons(QMessageBox.StandardButton.Yes)

            yes_btn = message.button(QMessageBox.StandardButton.Yes)
            yes_btn.setText("U redu")

            message.exec()
        else:
            self.__a_b_flag = True
            colors = self.__color_graph(neighbors_list)
            for node, clr in colors.items():
                for i in range(len(self.locations)):
                    if node == self.locations[i].get_name():
                        self.locations[i].set_color(f"{'yellow' if clr == 0 else 'red'}")
                        self.locations[i].set_kind(f"{'B' if clr == 0 else 'A'}")

            for link in self.links:
                for loc in self.locations:
                    if link.get_location1().get_name() == loc.get_name():
                        link.get_location1().set_kind(loc.get_kind())
                    if link.get_location2().get_name() == loc.get_name():
                        link.get_location2().set_kind(loc.get_kind())


            for link in self.links:
                if link.get_location1().get_kind() == 'A':
                    link.get_antenna1().set_kind('A')
                else:
                    link.get_antenna1().set_kind('B')

                if link.get_location2().get_kind() == 'A':
                    link.get_antenna2().set_kind('A')
                else:
                    link.get_antenna2().set_kind('B')

            self.__paint_on_map()

    def __color_graph(self, adjacency_list):
        color = {}
        for node in adjacency_list:
            if node not in color:
                queue = deque([node])
                color[node] = 0
                while queue:
                    current = queue.popleft()
                    current_color = color[current]
                    next_color = 1 - current_color
                    for neighbor in adjacency_list[current]:
                        if neighbor not in color:
                            color[neighbor] = next_color
                            queue.append(neighbor)
                        elif color[neighbor] == current_color:
                            return None
        return color

    def __form_network_tree(self):
        adjacency_list = {}
        for link in self.links:
            loc1 = link.get_location1().get_name()
            loc2 = link.get_location2().get_name()
            if loc1 not in adjacency_list:
                adjacency_list[loc1] = []
            if loc2 not in adjacency_list:
                adjacency_list[loc2] = []
            adjacency_list[loc1].append(loc2)
            adjacency_list[loc2].append(loc1)

        return adjacency_list

    def __has_odd_cycle(self, adjacency_list):
        def dfs(node, parent, depth):
            visited[node] = depth
            for neighbor in adjacency_list[node]:
                if neighbor not in visited:
                    if dfs(neighbor, node, depth + 1):
                        return True
                elif neighbor != parent and (depth - visited[neighbor]) % 2 == 0:
                    return True
            return False

        visited = {}
        for node in adjacency_list:
            if node not in visited:
                if dfs(node, None, 0):
                    return True
        return False

    def __calc_antennas_paint_cod(self, x1, y1, x2, y2):

        t1 = 0.1
        t2 = 0.9
        p1_x = x1 + t1 * (x2 - x1)
        p1_y = y1 + t1 * (y2 - y1)

        p2_x = x1 + t2 * (x2 - x1)
        p2_y = y1 + t2 * (y2 - y1)

        if x2 - x1 != 0:
            slope = (y2 - y1) / (x2 - x1)
            if slope != 0:
                perp_slope = -1 / slope
            else:
                perp_slope = 90
        else:
            perp_slope = 0

        length = 2

        if x2 - x1 != 0:
            dx = length / (1 + perp_slope ** 2) ** 0.5
            dy = perp_slope * dx
        else:
            dx = length
            dy = 0

        x3 = int(p1_x + dx)
        y3 = int(p1_y + dy)
        x4 = int(p1_x - dx)
        y4 = int(p1_y - dy)

        x5 = int(p2_x + dx)
        y5 = int(p2_y + dy)
        x6 = int(p2_x - dx)
        y6 = int(p2_y - dy)

        return x3, y3, x4, y4, x5, y5, x6, y6

    def __read_ant_file(self, name):
        gain = None
        HH = []
        HV = []
        VV = []
        VH = []
        ind_hh = None
        ind_hv = None
        ind_vv = None
        ind_vh = None
        with open(os.getcwd() + '\Antene\{}.txt'.format(name), 'r') as file:
            lines = file.readlines()
            count = 0
            for i in range(0, len(lines)):
                lines[i] = lines[i].strip().split(" ")
                if count == 0:
                    gain = lines[i][0]
                if lines[i][0] == "HH":
                    ind_hh = count
                elif lines[i][0] == "HV":
                    ind_hv = count
                elif lines[i][0] == "VV":
                    ind_vv = count
                elif lines[i][0] == "VH":
                    ind_vh = count
                count += 1
            for i in range(ind_hh + 1, ind_hv):
                var = [float(lines[i][0]), float(lines[i][-1])]
                HH.append(var)
            for i in range(ind_hv + 1, ind_vv):
                var = [float(lines[i][0]), float(lines[i][-1])]
                HV.append(var)
            for i in range(ind_vv + 1, ind_vh):
                var = [float(lines[i][0]), float(lines[i][-1])]
                VV.append(var)
            for i in range(ind_vh + 1, len(lines)):
                var = [float(lines[i][0]), float(lines[i][-1])]
                VH.append(var)
            return gain, HH, HV, VV, VH

    def __view_data_table(self):

        if self.ui.loc1_combo.currentText() == "" or self.ui.loc2_combo.currentText() == "" or self.ui.freq_linedit.text() == ""\
                or not( self.ui.cpol_ver_radiobtn.isChecked() or self.ui.cpol_hor_radiobtn.isChecked()) \
                or not( self.ui.xpol_ver_jmr_radiobtn.isChecked() or  self.ui.xpol_hor_jmr_radiobtn.isChecked())\
                or not (self.ui.xpol_ver_jmd_radiobtn.isChecked() or  self.ui.xpol_hor_jmd_radiobtn.isChecked()):

            message = QMessageBox()
            message.setWindowTitle("GREŠKA!!!")
            message.setText("Neispravno unešeni podaci!!!")
            message.setStandardButtons(QMessageBox.StandardButton.Yes)

            yes_btn = message.button(QMessageBox.StandardButton.Yes)
            yes_btn.setText("U redu")

            message.exec()
            return
        elif (self.ui.xpol_ver_jmr_radiobtn.isChecked() and self.ui.xpol_ver_jmd_radiobtn.isChecked()) or \
                (self.ui.xpol_hor_jmr_radiobtn.isChecked() and self.ui.xpol_hor_jmd_radiobtn.isChecked()):
            message = QMessageBox()
            message.setWindowTitle("GREŠKA!!!")
            message.setText("X-pol izabrane iste polarizacije antena!!!")
            message.setStandardButtons(QMessageBox.StandardButton.Yes)

            yes_btn = message.button(QMessageBox.StandardButton.Yes)
            yes_btn.setText("U redu")

            message.exec()
        else:
            ant1 = self.ui.loc1_combo.currentText()
            ant2 = self.ui.loc2_combo.currentText()

            ant1_ = None
            ant2_ = None

            ant1_type = None
            ant2_type = None

            loc1 = None
            loc2 = None

            lok11, lok12 = ant1.split("(Tx)=>")
            jammer_link = None
            jammed_link = None
            az_jammer = None
            az_jammed = None

            for link in self.links:
                if link.get_location1().get_name() == lok11 and link.get_location2().get_name() == lok12 or \
                        link.get_location2().get_name() == lok11 and link.get_location1().get_name() == lok12:
                    jammer_link = link.get_name()

                    if lok11 == link.get_location1().get_name():
                        ant1_ = link.get_antenna1()
                        loc1 = link.get_location1()
                        az_jammer = link.get_az12()
                        ant1_type = link.get_antenna1().kind_of_antena()
                    else:
                        ant1_ = link.get_antenna2()
                        loc1 = link.get_location2()
                        az_jammer = link.get_az21()
                        ant1_type = link.get_antenna2().kind_of_antena()

            lok21, lok22 = ant2.split("(Rx)=>")

            for link in self.links:
                if link.get_location1().get_name() == lok21 and link.get_location2().get_name() == lok22 or \
                        link.get_location2().get_name() == lok21 and link.get_location1().get_name() == lok22:
                    jammed_link = link.get_name()
                    if lok21 == link.get_location1().get_name():
                        ant2_ = link.get_antenna1()
                        loc2 = link.get_location1()
                        az_jammed = link.get_az12()
                        ant2_type = link.get_antenna1().kind_of_antena()
                    else:
                        ant2_ = link.get_antenna2()
                        loc2 = link.get_location2()
                        az_jammed = link.get_az21()
                        ant2_type = link.get_antenna2().kind_of_antena()



            if lok11 == lok21 and lok12 == lok22:
                message = QMessageBox()
                message.setWindowTitle("GREŠKA!!!")
                message.setText("Unešena je ista antena!!!")
                message.setStandardButtons(QMessageBox.StandardButton.Yes)

                yes_btn = message.button(QMessageBox.StandardButton.Yes)
                yes_btn.setText("U redu")

                message.exec()

            elif ant1_type == ant2_type:
                message = QMessageBox()
                message.setWindowTitle("GREŠKA!!!")
                message.setText("Unešene antene istog tipa!!!")
                message.setStandardButtons(QMessageBox.StandardButton.Yes)

                yes_btn = message.button(QMessageBox.StandardButton.Yes)
                yes_btn.setText("U redu")

                message.exec()

            elif jammer_link == jammed_link:
                message = QMessageBox()
                message.setWindowTitle("GREŠKA!!!")
                message.setText("Izabrane antene pripadaju istom linku!!!")
                message.setStandardButtons(QMessageBox.StandardButton.Yes)

                yes_btn = message.button(QMessageBox.StandardButton.Yes)
                yes_btn.setText("U redu")

                message.exec()

            else:
                if self.ui.cpol_ver_radiobtn.isChecked():
                    cpol_mod = "VV"
                    jammer_c = "V"
                    jammed_c = "V"
                else:
                    cpol_mod = "HH"
                    jammer_c = "H"
                    jammed_c = "H"

                if self.ui.xpol_ver_jmr_radiobtn.isChecked() and self.ui.xpol_hor_jmd_radiobtn.isChecked():
                    xpol_jmr_cpol = "VV"
                    xpol_jmr_xpol = "VH"
                    xpol_jmd_cpol = "HH"
                    xpol_jmd_xpol = "HV"
                    jammer_x = "V"
                    jammed_x = "H"
                else:
                    xpol_jmr_cpol = "HH"
                    xpol_jmr_xpol = "HV"
                    xpol_jmd_cpol = "VV"
                    xpol_jmd_xpol = "VH"
                    jammer_x = "H"
                    jammed_x = "V"


                freq = self.ui.freq_linedit.text()

                help_link = Link("help", loc1, ant1_, loc2, ant2_)
                distance = help_link.get_length()
                jammer_angle = abs(az_jammer - help_link.get_az12())
                jammed_angle = abs(az_jammed - help_link.get_az21())

                if jammer_angle > 180:
                    jammer_angle = 360 - jammer_angle

                if jammed_angle > 180:
                    jammed_angle = 360 - jammed_angle

                air_loss = 92.45 + 20 * math.log(float(freq), 10) + 20 * math.log(distance / 1000, 10)

                jammer_disc_c = ant1_.calc_discr(jammer_angle, cpol_mod)
                if jammer_disc_c < 0:
                    jammer_disc_c = -jammer_disc_c

                jammed_disc_c = ant2_.calc_discr(jammed_angle, cpol_mod)
                if jammed_disc_c < 0:
                    jammed_disc_c = -jammed_disc_c

                jammer_disc_x_cp =  ant1_.calc_discr(jammer_angle, xpol_jmr_cpol)
                if jammer_disc_x_cp < 0:
                    jammer_disc_x_cp = -jammer_disc_x_cp

                jammer_disc_x_xp =  ant1_.calc_discr(jammer_angle, xpol_jmr_xpol)
                if jammer_disc_x_xp < 0:
                    jammer_disc_x_xp = -jammer_disc_x_xp

                jammed_disc_x_cp = ant2_.calc_discr(jammed_angle, xpol_jmd_cpol)
                if jammed_disc_x_cp < 0:
                    jammed_disc_x_cp = -jammed_disc_x_cp

                jammed_disc_x_xp = ant2_.calc_discr(jammed_angle, xpol_jmd_xpol)
                if jammed_disc_x_xp < 0:
                    jammed_disc_x_xp = -jammed_disc_x_xp

                cpol_interference_level = float(ant1_.get_pwr()) - float(ant1_.get_loss()) + float(ant1_.get_gain()) -\
                    jammer_disc_c - air_loss + float(ant2_.get_gain()) - jammed_disc_c - float(ant2_.get_loss())

                xpol_interference_level = 10*math.log((10**((float(ant1_.get_pwr()) - float(ant1_.get_loss()) + float(ant1_.get_gain()) -
                    jammer_disc_x_cp - air_loss + float(ant2_.get_gain()) - jammed_disc_x_xp - float(ant2_.get_loss()))/10) +
                    10 ** ((float(ant1_.get_pwr()) - float(ant1_.get_loss()) + float(ant1_.get_gain()) -
                            jammer_disc_x_xp - air_loss + float(ant2_.get_gain()) - jammed_disc_x_cp - float(
                                ant2_.get_loss())) / 10)), 10)


                dialog = Dialog_table()
                dialog.ui.interference_table.setColumnWidth(0, 170)
                dialog.ui.interference_table.setColumnCount(4)
                dialog.ui.interference_table.setItem(0, 2, QTableWidgetItem("Ometač"))
                dialog.ui.interference_table.setItem(1,2, QTableWidgetItem(ant1))
                dialog.ui.interference_table.setItem(2,2, QTableWidgetItem("C-pol"))
                dialog.ui.interference_table.setItem(3, 2, QTableWidgetItem(freq))
                dialog.ui.interference_table.setItem(4, 2, QTableWidgetItem("{:.1f}".format(distance/1000)))
                dialog.ui.interference_table.setItem(5, 2, QTableWidgetItem(ant1_.get_pwr()))
                dialog.ui.interference_table.setItem(6, 2, QTableWidgetItem(ant1_.get_loss()))
                dialog.ui.interference_table.setItem(7, 2, QTableWidgetItem(ant1_.get_name()))
                dialog.ui.interference_table.setItem(8, 2, QTableWidgetItem(ant1_.get_gain()))
                dialog.ui.interference_table.setItem(9, 2, QTableWidgetItem("{:.2f}".format(jammer_angle)))
                dialog.ui.interference_table.setItem(10, 2, QTableWidgetItem("{:.2f}".format(jammer_disc_c)))
                dialog.ui.interference_table.setItem(11, 2, QTableWidgetItem("{:.3f}".format(air_loss)))

                dialog.ui.interference_table.setItem(12, 2, QTableWidgetItem(ant2_.get_name()))
                dialog.ui.interference_table.setItem(13, 2, QTableWidgetItem(ant2_.get_gain()))
                dialog.ui.interference_table.setItem(14, 2, QTableWidgetItem("{:.2f}".format(jammed_angle)))
                dialog.ui.interference_table.setItem(15, 2, QTableWidgetItem("{:.2f}".format(jammed_disc_c)))
                dialog.ui.interference_table.setItem(16, 2, QTableWidgetItem(ant2_.get_loss()))
                dialog.ui.interference_table.setItem(17, 2, QTableWidgetItem("{:.3f}".format(cpol_interference_level)))
                dialog.ui.interference_table.setItem(18, 2, QTableWidgetItem("{}-pol/{}-pol".format(jammer_c, jammed_c)))



                dialog.ui.interference_table.setItem(0, 3, QTableWidgetItem("Ometana \n stanica"))
                dialog.ui.interference_table.setItem(1, 3, QTableWidgetItem(ant2))
                dialog.ui.interference_table.setItem(2, 3, QTableWidgetItem("X-pol"))
                dialog.ui.interference_table.setItem(3, 3, QTableWidgetItem(freq))
                dialog.ui.interference_table.setItem(4, 3, QTableWidgetItem("{:.1f}".format(distance/1000)))
                dialog.ui.interference_table.setItem(5, 3, QTableWidgetItem(ant1_.get_pwr()))
                dialog.ui.interference_table.setItem(6, 3, QTableWidgetItem(ant1_.get_loss()))
                dialog.ui.interference_table.setItem(7, 3, QTableWidgetItem(ant1_.get_name()))
                dialog.ui.interference_table.setItem(8, 3, QTableWidgetItem(ant1_.get_gain()))
                dialog.ui.interference_table.setItem(9, 3, QTableWidgetItem("{:.2f}".format(jammer_angle)))
                dialog.ui.interference_table.setItem(10, 3, QTableWidgetItem("{:.2f}".format(jammer_disc_x_xp)))
                dialog.ui.interference_table.setItem(11, 3, QTableWidgetItem("{:.3f}".format(air_loss)))

                dialog.ui.interference_table.setItem(12, 3, QTableWidgetItem(ant2_.get_name()))
                dialog.ui.interference_table.setItem(13, 3, QTableWidgetItem(ant2_.get_gain()))
                dialog.ui.interference_table.setItem(14, 3, QTableWidgetItem("{:.2f}".format(jammed_angle)))
                dialog.ui.interference_table.setItem(15, 3, QTableWidgetItem("{:.2f}".format(jammed_disc_x_xp)))
                dialog.ui.interference_table.setItem(16, 3, QTableWidgetItem(ant2_.get_loss()))
                dialog.ui.interference_table.setItem(17, 3, QTableWidgetItem("{:.3f}".format(xpol_interference_level)))
                dialog.ui.interference_table.setItem(18, 3,
                                                     QTableWidgetItem("{}-pol/{}-pol".format(jammer_x, jammed_x)))

                dialog.exec()

    def __distance(self, loc1, loc2):
        return math.sqrt((loc2.get_x_coordinate() - loc1.get_x_coordinate())**2 + \
                         (loc2.get_y_coordinate() - loc1.get_y_coordinate())**2)

    def __add_antennas_to_combos(self):
        self.ui.loc1_combo.clear()
        self.ui.loc2_combo.clear()
        self.ui.loc1_combo.addItem("")
        self.ui.loc2_combo.addItem("")
        for i in range(len(self.links)):
            self.ui.loc1_combo.addItem("{0}(Tx)=>{1}".format(self.links[i].get_location1().get_name(),
                                                             self.links[i].get_location2().get_name()))
            self.ui.loc1_combo.addItem("{1}(Tx)=>{0}".format(self.links[i].get_location1().get_name(),
                                                             self.links[i].get_location2().get_name()))
            self.ui.loc2_combo.addItem("{0}(Rx)=>{1}".format(self.links[i].get_location1().get_name(),
                                                             self.links[i].get_location2().get_name()))
            self.ui.loc2_combo.addItem("{1}(Rx)=>{0}".format(self.links[i].get_location1().get_name(),
                                                             self.links[i].get_location2().get_name()))

    def __change_ant1_color(self, text):
        if not self.__a_b_flag:
            if self.ui.loc1_combo.currentText() != "":
                message = QMessageBox()
                message.setWindowTitle("GREŠKA!!!")
                message.setText("Ne može se izabrati stanica \n (proračunati A i B stanice)!!!")
                message.setStandardButtons(QMessageBox.StandardButton.Yes)

                yes_btn = message.button(QMessageBox.StandardButton.Yes)
                yes_btn.setText("U redu")

                message.exec()
                self.ui.loc1_combo.setCurrentIndex(0)

        else:
            self.__reset_ant_colors()

            if self.ui.loc2_combo.currentText() != "":

                text_ = self.ui.loc2_combo.currentText()
                lok1, lok2 = text_.split("(Rx)=>")

                for link in self.links:
                    if link.get_location1().get_name() == lok1 and link.get_location2().get_name() == lok2 or \
                            link.get_location2().get_name() == lok1 and link.get_location1().get_name() == lok2:
                        if lok1 == link.get_location1().get_name():
                            link.get_antenna1().set_color("yellow")
                        else:
                            link.get_antenna2().set_color("yellow")

            if text != "":
                lok1, lok2 = text.split("(Tx)=>")

                for link in self.links:
                    if link.get_location1().get_name() == lok1 and link.get_location2().get_name() == lok2 or \
                            link.get_location2().get_name() == lok1 and link.get_location1().get_name() == lok2:
                        if lok1 == link.get_location1().get_name():
                            link.get_antenna1().set_color("yellow")
                        else:
                            link.get_antenna2().set_color("yellow")
            self.__paint_on_map()

    def __change_ant2_color(self, text):
        if not self.__a_b_flag:
            if self.ui.loc2_combo.currentText() != "":
                message = QMessageBox()
                message.setWindowTitle("GREŠKA!!!")
                message.setText("Ne može se izabrati stanica \n (proračunati A i B stanice)!!!")
                message.setStandardButtons(QMessageBox.StandardButton.Yes)

                yes_btn = message.button(QMessageBox.StandardButton.Yes)
                yes_btn.setText("U redu")

                message.exec()
                self.ui.loc2_combo.setCurrentIndex(0)

        else:
            self.__reset_ant_colors()

            if self.ui.loc1_combo.currentText() != "":
                text_ = self.ui.loc1_combo.currentText()
                lok1, lok2 = text_.split("(Tx)=>")

                for link in self.links:
                    if link.get_location1().get_name() == lok1 and link.get_location2().get_name() == lok2 or \
                            link.get_location2().get_name() == lok1 and link.get_location1().get_name() == lok2:
                        if lok1 == link.get_location1().get_name():
                            link.get_antenna1().set_color("yellow")
                        else:
                            link.get_antenna2().set_color("yellow")

            if text != "":
                lok1, lok2 = text.split("(Rx)=>")

                for link in self.links:
                    if link.get_location1().get_name() == lok1 and link.get_location2().get_name() == lok2 or \
                            link.get_location2().get_name() == lok1 and link.get_location1().get_name() == lok2:
                        if lok1 == link.get_location1().get_name():
                            link.get_antenna1().set_color("yellow")
                        else:
                            link.get_antenna2().set_color("yellow")
            self.__paint_on_map()

    def __reset_ant_colors(self):

        for link in self.links:
            link.get_antenna1().set_color("blue")
            link.get_antenna2().set_color("blue")

    def __reset_loc_colors(self):
        for loc in self.locations:
            loc.set_color("red")



def app():

    app = QtWidgets.QApplication(sys.argv)
    win = window()
    win.show()
    sys.exit(app.exec())


app()