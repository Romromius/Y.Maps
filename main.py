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

        self.img = QLabel(self)
        self.img.setText('Загрузка/Введите новый запрос')
        self.img.resize(600, 600)

        self.search_place = QLineEdit(self)
        self.search_place.setGeometry(100, 20, 300, 30)
        self.search_place.clearFocus()

        self.search_btn = QPushButton(self)
        self.search_btn.setGeometry(420, 10, 50, 50)
        self.search_btn.setText("""_\n( _ )\n\\""")
        self.search_btn.clicked.connect(self.search)

        self.view_btn = QPushButton(self)
        self.view_btn.setGeometry(500, 10, 50, 50)
        self.view_btn.setText("map/1")
        self.view_btn.clicked.connect(self.switch)

        self.map_move_x = 0
        self.map_move_y = 0

        self.map_spn = 1
        self.map_file = None
        self.coords = (0, 0)
        # self.search('Vladivostok')

    def switch(self):
        view = int(self.view_btn.text().split("/")[1])
        self.view_btn.setText(self.sp[view ^ 1 ^ 2 ^ 3] + f"/{(view + 1) % 3}")

    def search(self, toponym):
        try:
            toponym = toponym if len(self.search_place.text()) == 0 else "+".join(self.search_place.text().split())
            geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={toponym}&format=json"
            response = requests.get(geocoder_request)
            json_response = response.json()
            coords = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"].split()
        except IndexError:
            self.speaker.say('bad beep', 'error', 'search error')
            self.img.setText('Ошибка поиска!')
            return
        except requests.exceptions.ConnectionError:
            self.speaker.say('bad beep', 'error', 'no net')
            self.img.setText('Нет сети!')
            return

        self.map_file = "map.png"

        self.coords = coords
        self.update_map()

    def update_map(self):
        view = self.view_btn.text().split('/')[0]
        x, y = float(self.coords[0]) + self.map_move_x, float(self.coords[1]) + self.map_move_y
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={x},{y}&spn={self.map_spn},{self.map_spn}&l={view}&z=15&l=map&pt={self.coords[0]},{self.coords[1]},pm2rdm"
        try:
            response = requests.get(map_request)
        except requests.exceptions.ConnectionError:
            self.speaker.say('bad beep', 'error', 'no net')
            self.img.setText('Нет сети!')
            return
        if not response:
            sys.exit(1)
        with open(self.map_file, "wb") as file:
            file.write(response.content)
        if random.randint(0, 1):
            self.speaker.say('good beep', 'request get')
        self.img.setPixmap(QPixmap(self.map_file))

    def keyPressEvent(self, event):
        if event.key() == 45:
            self.map_spn -= 1
            self.update_map()
        elif event.key() == 61:
            self.map_spn += 1
            self.update_map()
        elif event.key() == 16777235:  # up
            self.map_move_y += 0.25 + self.map_spn
            self.update_map()
        elif event.key() == 16777237:  # down
            self.map_move_y -= 0.25 + self.map_spn
            self.update_map()
        elif event.key() == 16777234:  # left
            self.map_move_x -= 0.25 + self.map_spn
            self.update_map()
        elif event.key() == 16777236:  # right
            self.map_move_x += 0.25 + self.map_spn
            self.update_map()
        print(self.map_spn)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Map()
    ex.show()
    sys.exit(app.exec())