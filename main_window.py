"""
Модуль main_window.py — графическое приложение для просмотра датасета изображений.
"""

import sys
import os
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout,
    QHBoxLayout, QWidget, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QPixmap, QResizeEvent
from PyQt5.QtCore import Qt
from script import ImgPathIterator


class ImageViewerWindow(QMainWindow):
    """
    Главное окно приложения для просмотра изображений.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Обзор на свинье")
        self.setGeometry(100, 100, 800, 600)

        self.iterator: Optional[ImgPathIterator] = None
        self.image_label: Optional[QLabel] = None
        self.status_bar = self.statusBar()

        self._init_ui()

    def _init_ui(self) -> None:
        """Инициализирует пользовательский интерфейс."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        source_layout = QHBoxLayout()
        btn_select_folder = QPushButton("Выбрать папку с изображениями")
        btn_select_csv = QPushButton("Выбрать CSV-аннотацию")

        btn_select_folder.clicked.connect(self._select_folder)
        btn_select_csv.clicked.connect(self._select_csv)

        source_layout.addWidget(btn_select_folder)
        source_layout.addWidget(btn_select_csv)
        layout.addLayout(source_layout)

        nav_layout = QHBoxLayout()
        btn_prev = QPushButton("← Предыдущее")
        btn_next = QPushButton("Следующее →")

        btn_prev.clicked.connect(self._show_previous_image)
        btn_next.clicked.connect(self._show_next_image)

        nav_layout.addWidget(btn_prev)
        nav_layout.addWidget(btn_next)
        layout.addLayout(nav_layout)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("Загрузите изображения")
        self.image_label.setStyleSheet("background-image:url(background_img.gif); font-size: 14px;")
        layout.addWidget(self.image_label)

        self.status_bar.showMessage("Выберите источник данных...")

        central_widget.setLayout(layout)

    def _load_paths(self, source: str) -> None:
        """Загружает пути через ImgPathIterator."""
        try:
            self.iterator = ImgPathIterator(source)
            if len(self.iterator) == 0:
                raise ValueError("Нет изображений для отображения.")
            self.status_bar.showMessage(f"Загружено {len(self.iterator)} изображений")
            self._show_current_image()
        except (OSError, ValueError) as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные:\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "Неизвестная ошибка", str(e))

    def _select_folder(self) -> None:
        folder: str = QFileDialog.getExistingDirectory(
            self, "Выберите папку с изображениями"
        )
        if folder:
            self._load_paths(folder)

    def _select_csv(self) -> None:
        csv_file, _ = QFileDialog.getOpenFileName(
            self, "Выберите CSV-файл", "", "CSV Files (*.csv)"
        )
        if csv_file:
            self._load_paths(csv_file)

    def _show_current_image(self) -> None:
        if not self.iterator:
            self._show_placeholder("Нет данных для отображения.")
            return

        try:
            path = self.iterator.current()
        except (IndexError, StopIteration):
            self._show_placeholder("Нет изображений.")
            return

        pixmap = QPixmap(path)
        if pixmap.isNull():
            self._show_placeholder(f"Не удалось загрузить: {os.path.basename(path)}")
            return

        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setStyleSheet("background-image:url(background_data.jpg)")
        self.status_bar.showMessage(
            f"Изображение {self.iterator._index + 1} из {len(self.iterator)}: {os.path.basename(path)}"
        )

    def _show_placeholder(self, text: str) -> None:
        """
        Отображает заглушку вместо изображения.

        Args:
            text (str): Текст для отображения.
        """
        if self.image_label:
            self.image_label.setText(text)
            self.image_label.setPixmap(QPixmap())
            self.image_label.setStyleSheet("background-image:url(background_data.jpg); font-size: 14px;")

    def _show_next_image(self) -> None:
        if not self.iterator:
            return
        try:
            self.iterator.next()
            self._show_current_image()
        except StopIteration:
            pass

    def _show_previous_image(self) -> None:
        if not self.iterator:
            return
        try:
            self.iterator.prev()
            self._show_current_image()
        except StopIteration:
            pass

    def _show_placeholder(self, text: str) -> None:
        if self.image_label:
            self.image_label.setText(text)
            self.image_label.setPixmap(QPixmap())
            self.image_label.setStyleSheet("background-image:url(background_data.jpg); font-size: 14px;")

    def resizeEvent(self, event: QResizeEvent) -> None:
        if self.iterator:
            self._show_current_image()
        super().resizeEvent(event)


def main() -> None:
    """
    Точка входа в приложение.
    """
    try:
        app = QApplication(sys.argv)
        window = ImageViewerWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Критическая ошибка при запуске приложения: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
