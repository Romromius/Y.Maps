import json
import os
import random
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QLabel
import requests
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from speaker import Speaker


class Map(QMainWindow):
    def __init__(self):
        super().__init__()
        self.speaker = Speaker()
        self.setWindowTitle("картка")
        self.setFixedSize(600, 520)

        self.sp = ["map", "sat", "sat,skl"]
        self.view = "map"

        self.img = QLabel(self)
        self.img.setText('Загрузка/Введите новый запрос')
        self.img.setAlignment(QtCore.Qt.AlignCenter)
        self.img.resize(600, 600)

        self.search_place = QLineEdit(self)
        self.search_place.setGeometry(5, 0, 330, 30)
        self.search_place.returnPressed.connect(lambda: self.search(self.search_place.text()))

        self.search_data = QLabel(self)
        self.search_data.setGeometry(15, 30, 330, 30)
        self.search_data.setText("Adress:")
        self.search_data.setWordWrap(True)

        self.search_btn = QPushButton(self)
        self.search_btn.setGeometry(370, 10, 50, 50)
        self.search_btn.setText("""_\n( _ )\n\\""")
        self.search_btn.clicked.connect(self.search)

        self.view_btn = QPushButton(self)
        self.view_btn.setGeometry(440, 10, 50, 50)
        self.view_btn.setText("map/1")
        self.view_btn.clicked.connect(self.switch)

        self.index_lbl = QLabel(self)
        self.index_lbl.setGeometry(520, 60, 50, 20)
        self.index_lbl.setText("On")

        self.index_btn = QPushButton(self)
        self.index_btn.setGeometry(500, 10, 50, 50)
        self.index_btn.setText("Index")
        self.index_btn.clicked.connect(self.switch_index)

        self.clear_btn = QPushButton(self)
        self.clear_btn.setGeometry(550, 10, 50, 50)
        self.clear_btn.setText("clear")
        self.clear_btn.clicked.connect(self.clear)

        self.clear_fl = 0
        self.point = None
        self.show_index = True
        self.searched_adress = ''
        self.searched_index = ''

        self.coords = (0, 0)

        self.map_spn = 1
        self.map_file = None

        # self.search('Vladivostok')

    def switch_index(self):
        self.show_index = not self.show_index
        match self.show_index:
            case True:
                self.index_lbl.setText('On')
                self.speaker.say('good beep')
            case False:
                self.index_lbl.setText('Off')
                self.speaker.say('neutral beep')
        self.update_map()


    def clear(self):
        self.clear_fl = 1
        self.search_data.setText(f"Adress:")
        self.point = None
        self.update_map()

    def switch(self):
        view = int(self.view_btn.text().split("/")[1])
        self.view_btn.setText(self.sp[view ^ 1 ^ 2 ^ 3] + f"/{(view + 1) % 3}")
        self.view = self.view_btn.text().split('/')[0]
        try:
            self.update_map()
        except Exception:
            pass

    def search(self, toponym):
        try:
            if len(self.search_place.text()) == 0:
                toponym = toponym
            else:
                toponym = "+".join(self.search_place.text().split())
            geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={toponym}&format=json"
            response = requests.get(geocoder_request)
            json_response = response.json()
            self.coords = [float(i) for i in json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"].split()]
            self.point = self.coords
            data = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["Address"]["formatted"]
            self.searched_adress = f"Adress: {data}"
            try:
                self.searched_index = json_response['response']['GeoObjectCollection']['featureMember'][0][
                    'GeoObject']['metaDataProperty']['GeocoderMetaData']['Address'][
                    'postal_code']
            except KeyError:
                self.searched_index = ''

        except IndexError:
            self.speaker.say('bad beep', 'error', 'search error', important=True)
            self.img.setText('Ошибка поиска!')
            return
        except requests.exceptions.ConnectionError:
            self.speaker.say('bad beep', 'error', 'no net', important=True)
            self.img.setText('Нет сети!')
            return
        self.map_file = "map.png"
        self.speaker.say('neutral beep', 'request get')

        self.update_map()

    def update_map(self):
        params = {"ll": f"{self.coords[0]},{self.coords[1]}",
                  "l": self.view,
                  "z": self.map_spn}
        if self.point:
            params["pt"] = f'{self.point[0]},{self.point[1]},ya_ru'
        try:
            response = requests.get(f'http://static-maps.yandex.ru/1.x/', params=params)
            # response = requests.get(f'http://static-maps.yandex.ru/1.x/?ll={x},{y}&l={self.view}&z={self.map_spn}&pt={self.point[0]},{self.point[1]},pm2rdm', params=params)
        except requests.exceptions.ConnectionError:
            self.speaker.say('bad beep', 'error', 'no net', important=True)
            self.img.setText('Нет сети!')
            return
        if not response:
            sys.exit(1)
        with open('map.png', "wb") as file:
            file.write(response.content)
        self.img.setPixmap(QPixmap(self.map_file))

        # if self.show_index:
        #     try:
        #         self.search_data.setText(self.searched_adress + ', ' +
        #                                  self.searched_index)
        #     except KeyError:
        #         self.searched_index = ''
        # else:
        #     self.searched_index = ''

        if self.show_index and self.searched_index:
            self.search_data.setText(f'{self.searched_adress}, {self.searched_index}')
        else:
            self.search_data.setText(self.searched_adress)

    def mousePressEvent(self, a0):
        self.search_place.clearFocus()

    def keyPressEvent(self, event):
        match event.key():
            case 45:
                self.map_spn -= 1
            case 61:
                self.map_spn += 1
            case 16777235:  # up
                self.coords[1] += 10
            case 16777237:  # down
                self.coords[1] -= 10
            case 16777234:  # left
                self.coords[0] -= 10
            case 16777236:  # right
                self.coords[0] += 10
            case _:
                return

        if self.map_spn <= 0:
            self.speaker.say('bad beep')
            self.map_spn = 1
            return
        elif self.map_spn >= 22:
            self.speaker.say('bad beep')
            self.map_spn = 21
            return

        self.update_map()
        print(self.coords)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Map()
    ex.show()
    sys.exit(app.exec())