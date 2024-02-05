import json
import os
import random
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QLabel
import requests
from PyQt5.QtGui import QPixmap
from speaker import Speaker


class Map(QMainWindow):
    def __init__(self):
        super().__init__()
        self.speaker = Speaker()
        self.setWindowTitle("картка")
        self.setFixedSize(600, 600)

        self.sp = ["map", "sat", "sat,skl"]
        self.view = "map"

        self.img = QLabel(self)
        self.img.setText('Загрузка/Введите новый запрос')
        self.img.resize(600, 600)

        self.search_place = QLineEdit(self)
        self.search_place.setGeometry(100, 20, 300, 30)
        self.search_place.returnPressed.connect(lambda: self.search(self.search_place.text()))
        self.search_place.returnPressed.connect(self.search_place.clearFocus)

        self.search_btn = QPushButton(self)
        self.search_btn.setGeometry(410, 10, 50, 50)
        self.search_btn.setText("""_\n( _ )\n\\""")
        self.search_btn.clicked.connect(self.search)

        self.view_btn = QPushButton(self)
        self.view_btn.setGeometry(470, 10, 100, 50)
        self.view_btn.setText("map/1")
        self.view_btn.clicked.connect(self.switch)

        self.map_move_x = 0
        self.map_move_y = 0

        self.map_spn = 1
        self.map_file = None
        self.coords = (0, 0)
        self.point = None

    def switch(self):
        view = int(self.view_btn.text().split("/")[1])
        self.view_btn.setText(self.sp[view ^ 1 ^ 2 ^ 3] + f"/{(view + 1) % 3}")
        self.view = self.view_btn.text().split('/')[0]
        self.update_map()

    def search(self, toponym):
        try:
            if len(self.search_place.text()) == 0:
                toponym = toponym
            else:
                toponym = "+".join(self.search_place.text().split())
            geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={toponym}&format=json"
            response = requests.get(geocoder_request)
            json_response = response.json()
            coords = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"].split()
            self.point = coords
        except IndexError:
            self.speaker.say('bad beep', 'error', 'search error', important=True)
            self.img.setText('Ошибка поиска!')
            return
        except requests.exceptions.ConnectionError:
            self.speaker.say('bad beep', 'error', 'no net', important=True)
            self.img.setText('Нет сети!')
            return

        self.map_file = "map.png"

        self.coords = coords
        self.update_map()

    def update_map(self):
        x, y = float(self.coords[0]) + self.map_move_x, float(self.coords[1]) + self.map_move_y
        params = {"ll": f"{x},{y}",
                  "l": self.view,
                  "z": self.map_spn}
        if self.point:
            params["pt"] = f'{self.point[0]},{self.point[1]},pm2rdm'
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
        if random.random() < 0.1:
            self.speaker.say('request get')
        self.img.setPixmap(QPixmap(self.map_file))

    def mousePressEvent(self, a0):
        self.search_place.clearFocus()

    def keyPressEvent(self, event):
        match event.key():
            case 45:
                self.map_spn -= 1
            case 61:
                self.map_spn += 1
            case 16777235:  # up
                self.map_move_y += 0.25 + self.map_spn
            case 16777237:  # down
                self.map_move_y -= 0.25 + self.map_spn
            case 16777234:  # left
                self.map_move_x -= 0.25 + self.map_spn
            case 16777236:  # right
                self.map_move_x += 0.25 + self.map_spn
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
        print(self.map_spn)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Map()
    ex.show()
    sys.exit(app.exec())
