import sys
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QWidget, QApplication, QMainWindow, QPushButton, QVBoxLayout
from main import ScreenRecorder


class MainWindow(QMainWindow):
    recorder = ScreenRecorder()

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setFixedSize(QSize(350, 150))

        layout = QVBoxLayout()
        self.setWindowTitle("Приложение для записи экрана")
        self.button_1 = QPushButton("Начать запись")
        self.button_1.clicked.connect(self.the_button1_was_clicked)
        layout.addWidget(self.button_1)

        self.button_2 = QPushButton("Остановить запись")
        self.button_2.clicked.connect(self.the_button2_was_clicked)
        layout.addWidget(self.button_2)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def the_button1_was_clicked(self):
        print("Clicked!")
        self.button_1.setText('Идет запись экрана')
        self.recorder.start_recording()

    def the_button2_was_clicked(self):
        self.button_1.setText('Начать запись')
        self.recorder.stop_recording()
        print("Запись завершена")


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
