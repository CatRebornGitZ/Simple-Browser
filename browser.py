import sys
import json
from PyQt5.QtCore import QUrl, QSettings
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLineEdit,
    QToolBar,
    QAction,
    QDialog,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
    QListWidget,
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon, QPalette, QColor

# Класс окна настроек
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setGeometry(200, 200, 300, 200)

        # Настройки
        self.settings = QSettings("SimpleBrowser", "Settings")

        # Создаем layout
        layout = QVBoxLayout()

        # DNS сервер
        dns_label = QLabel("DNS сервер:")
        self.dns_input = QLineEdit(self.settings.value("dns", "8.8.8.8"))
        layout.addWidget(dns_label)
        layout.addWidget(self.dns_input)

        # Выбор языка
        language_label = QLabel("Язык:")
        self.language_combo = QComboBox()
        self.language_combo.addItem("Русский", "ru")
        self.language_combo.addItem("Английский", "en")
        current_lang = self.settings.value("language", "ru")
        index = self.language_combo.findData(current_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        layout.addWidget(language_label)
        layout.addWidget(self.language_combo)

        # Выбор темы
        theme_label = QLabel("Тема:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Светлая", "light")
        self.theme_combo.addItem("Темная", "dark")
        current_theme = self.settings.value("theme", "light")
        index = self.theme_combo.findData(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        layout.addWidget(theme_label)
        layout.addWidget(self.theme_combo)

        # Кнопки "Сохранить" и "Отмена"
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.close)
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def save_settings(self):
        # Сохраняем настройки
        self.settings.setValue("dns", self.dns_input.text())
        self.settings.setValue("language", self.language_combo.currentData())
        self.settings.setValue("theme", self.theme_combo.currentData())
        QMessageBox.information(self, "Сохранено", "Настройки успешно сохранены!")
        self.close()

# Класс окна истории
class HistoryDialog(QDialog):
    def __init__(self, history, parent=None):
        super().__init__(parent)
        self.setWindowTitle("История")
        self.setGeometry(200, 200, 400, 300)

        # Создаем layout
        layout = QVBoxLayout()

        # Список истории
        self.history_list = QListWidget()
        self.update_history(history)
        layout.addWidget(self.history_list)

        # Кнопка "Очистить историю"
        clear_btn = QPushButton("Очистить историю")
        clear_btn.clicked.connect(self.clear_history)
        layout.addWidget(clear_btn)

        self.setLayout(layout)

    def update_history(self, history):
        # Обновляем список истории
        self.history_list.clear()
        for item in history:
            self.history_list.addItem(item)

    def clear_history(self):
        # Очищаем историю
        self.history_list.clear()
        QMessageBox.information(self, "Очищено", "История очищена!")
        self.parent().clear_history()

# Основной класс браузера
class SimpleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        # Настройки
        self.settings = QSettings("SimpleBrowser", "Settings")

        # История
        self.history = self.load_history()

        # Создаем QWebEngineView для отображения веб-страниц
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.google.com"))

        # Создаем поле для ввода URL
        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)

        # Создаем тулбар
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Кнопка "Назад"
        back_btn = QAction(QIcon.fromTheme("go-previous"), "Назад", self)
        back_btn.triggered.connect(self.browser.back)
        toolbar.addAction(back_btn)

        # Кнопка "Вперед"
        forward_btn = QAction(QIcon.fromTheme("go-next"), "Вперед", self)
        forward_btn.triggered.connect(self.browser.forward)
        toolbar.addAction(forward_btn)

        # Кнопка "Обновить"
        reload_btn = QAction(QIcon.fromTheme("reload"), "Обновить", self)
        reload_btn.triggered.connect(self.browser.reload)
        toolbar.addAction(reload_btn)

        # Кнопка "Настройки"
        settings_btn = QAction(QIcon.fromTheme("preferences-system"), "Настройки", self)
        settings_btn.triggered.connect(self.open_settings)
        toolbar.addAction(settings_btn)

        # Кнопка "История"
        history_btn = QAction(QIcon.fromTheme("document-open-recent"), "История", self)
        history_btn.triggered.connect(self.open_history)
        toolbar.addAction(history_btn)

        # Добавляем поле ввода URL в тулбар
        toolbar.addWidget(self.urlbar)

        # Устанавливаем браузер как центральный виджет
        self.setCentralWidget(self.browser)

        # Обновляем URL в поле ввода при изменении страницы
        self.browser.urlChanged.connect(self.update_urlbar)

        # Применяем сохраненные настройки
        self.apply_settings()

    def navigate_to_url(self):
        # Получаем текст из поля ввода и переходим по URL
        url = self.urlbar.text()
        if not url.startswith(("http://", "https://")):
            url = "http://" + url
        self.browser.setUrl(QUrl(url))

        # Добавляем URL в историю
        self.add_to_history(url)

    def update_urlbar(self, q):
        # Обновляем поле ввода URL при изменении страницы
        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)

    def open_settings(self):
        # Открываем окно настроек
        dialog = SettingsDialog(self)
        dialog.exec_()
        self.apply_settings()

    def apply_settings(self):
        # Применяем DNS (в реальности это требует дополнительной реализации)
        dns = self.settings.value("dns", "8.8.8.8")
        print(f"Используемый DNS: {dns}")

        # Применяем тему
        theme = self.settings.value("theme", "light")
        self.set_theme(theme)

    def set_theme(self, theme):
        # Устанавливаем светлую или темную тему
        palette = QApplication.palette()
        if theme == "dark":
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
            palette.setColor(QPalette.Base, QColor(35, 35, 35))
            palette.setColor(QPalette.Text, QColor(255, 255, 255))
        else:
            palette.setColor(QPalette.Window, QColor(255, 255, 255))
            palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
            palette.setColor(QPalette.Base, QColor(255, 255, 255))
            palette.setColor(QPalette.Text, QColor(0, 0, 0))
        QApplication.setPalette(palette)

    def add_to_history(self, url):
        # Добавляем URL в историю
        if url not in self.history:
            self.history.append(url)
            self.save_history()

    def load_history(self):
        # Загружаем историю из файла
        try:
            with open("history.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def save_history(self):
        # Сохраняем историю в файл
        with open("history.json", "w") as file:
            json.dump(self.history, file)

    def clear_history(self):
        # Очищаем историю
        self.history.clear()
        self.save_history()

    def open_history(self):
        # Открываем окно истории
        dialog = HistoryDialog(self.history, self)
        dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleBrowser()
    window.setWindowTitle("Simple Browser")
    window.show()
    sys.exit(app.exec_())