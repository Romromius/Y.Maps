import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QLabel
import requests
from PyQt5.QtGui import QPixmap


class Map(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("картка")
        self.setGeometry(350, 350, 600, 600)

        ZAPROS = "Владивосток"
        geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={ZAPROS}&format=json"
        response = requests.get(geocoder_request)
        json_response = response.json()
        coords = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"][
            "pos"].split()

        map_request = f"http://static-maps.yandex.ru/1.x/?ll={coords[0]},{coords[1]}&spn=30,30&l=map"
        response = requests.get(map_request)
        if not response:
            sys.exit(1)
        map_file = "map.png"
        with open(map_file, "wb") as file:
            file.write(response.content)

        self.pix = QPixmap(map_file)
        self.img = QLabel(self)
        self.img.resize(600, 600)
        self.img.setPixmap(self.pix)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Map()
    ex.show()
    sys.exit(app.exec())