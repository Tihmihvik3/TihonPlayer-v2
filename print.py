from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt6.QtGui import QIcon
import sys

# Создаём приложение
app = QApplication(sys.argv)

# Создаём главное окно
window = QWidget()
window.setWindowTitle("Пример с кнопками")

# Создаём компоновщик
layout = QVBoxLayout()

# Создаём кнопки
button1 = QPushButton()
button2 = QPushButton("Кнопка 2")
button3 = QPushButton("Кнопка 3")

# Устанавливаем иконки для кнопок
button1.setIcon(QIcon("icons/stop.png"))
button2.setIcon(QIcon("icons/play.png"))

# Устанавливаем размер кнопок
button1.setFixedSize(30, 30)
button2.setFixedSize(30, 30)

# Растягиваем иконку на всю кнопку
button1.setIconSize(button1.size())

# Добавляем кнопки в компоновщик
layout.addWidget(button1)
layout.addWidget(button2)
layout.addWidget(button3)

# Устанавливаем компоновщик для окна
window.setLayout(layout)

# Показываем окно
window.show()

# Запускаем цикл событий
app.exec()