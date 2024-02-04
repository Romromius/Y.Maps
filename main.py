import os
import sys
import PyQt5.QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QLabel
import requests
from PyQt5.QtGui import QPixmap
from speaker import Speaker


class Map(QMainWindow):
    def __init__(self):
        super().__init__()
        self.speaker = Speaker()
        self.setWindowTitle("картка")
        self.setGeometry(350, 350, 600, 600)

        self.img = QLabel(self)
        self.img.setText('Загрузка')
        self.img.resize(600, 600)

        self.map_move_x = 0
        self.map_move_y = 0

        self.map_spn = 1
        self.map_file = None
        self.coords = (0, 0)
        self.search('Vladivostok')

    def search(self, toponym):
        try:
            geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={toponym}&format=json"
            response = requests.get(geocoder_request)
            json_response = response.json()
            coords = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"].split()
        except IndexError:
            self.speaker.say('bad beep', 'error', 'search error')
            self.img.setText('Ошибка!')
            return

        self.map_file = "map.png"

        self.coords = coords
        self.update_map()

    def update_map(self):
        x, y = float(self.coords[0]) + self.map_move_x, float(self.coords[1]) + self.map_move_y
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={x},{y}&spn={self.map_spn},{self.map_spn}&l=map"
        response = requests.get(map_request)
        if not response:
            sys.exit(1)
        with open(self.map_file, "wb") as file:
            file.write(response.content)
        self.speaker.say('bad beep', 'request get')
        self.img.setPixmap(QPixmap(self.map_file))

    def keyPressEvent(self, event):
        if event.key() == 45:
            self.map_spn -= 0.7
            self.update_map()
        elif event.key() == 61:
            self.map_spn += 0.7
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