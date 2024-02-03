import os
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
        self.setGeometry(350, 350, 600, 600)

        self.img = QLabel(self)
        self.img.setText('Загрузка')
        self.img.resize(600, 600)

        self.search('Владивосток')

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

        map_request = f"http://static-maps.yandex.ru/1.x/?ll={coords[0]},{coords[1]}&spn=30,30&l=map"
        response = requests.get(map_request)
        self.speaker.say('bad beep', 'request get')
        if not response:
            sys.exit(1)
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)
        self.img.setPixmap(QPixmap(self.map_file))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Map()
    ex.show()
    sys.exit(app.exec())