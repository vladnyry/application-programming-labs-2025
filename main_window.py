"""
Модуль main_window.py — графическое приложение для просмотра датасета изображений.

Позволяет:
- Выбирать папку с изображениями или CSV-файл аннотации;
- Просматривать изображения по одному с сохранением пропорций;
- Навигация: «Предыдущее» / «Следующее».

Использует класс ImgPathIterator из модуля script (лабораторная работа №2).
"""

import sys
import os
from typing import List, Optional
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
        """Инициализирует главное окно и его атрибуты."""
        super().__init__()
        self.setWindowTitle("Обзор на свиней")
        self.setGeometry(100, 100, 800, 600)

        # Атрибуты данных
        self.image_paths: List[str] = []
        self.current_index: int = 0
        self.current_image_path: Optional[str] = None

        # UI-компоненты
        self.image_label: Optional[QLabel] = None
        self.status_bar = self.statusBar()

        # Инициализация интерфейса
        self._init_ui()

    def _init_ui(self) -> None:
        """Инициализирует пользовательский интерфейс."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # Кнопки выбора источника
        source_layout = QHBoxLayout()
        btn_select_folder = QPushButton("Выбрать папку с изображениями")
        btn_select_csv = QPushButton("Выбрать CSV-аннотацию")

        btn_select_folder.clicked.connect(self._select_folder)
        btn_select_csv.clicked.connect(self._select_csv)

        source_layout.addWidget(btn_select_folder)
        source_layout.addWidget(btn_select_csv)
        layout.addLayout(source_layout)

        # Кнопки навигации
        nav_layout = QHBoxLayout()
        btn_prev = QPushButton("← Предыдущее")
        btn_next = QPushButton("Следующее →")

        btn_prev.clicked.connect(self._show_previous_image)
        btn_next.clicked.connect(self._show_next_image)

        nav_layout.addWidget(btn_prev)
        nav_layout.addWidget(btn_next)
        layout.addLayout(nav_layout)

        # Метка для изображения
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("Загрузите изображения")
        self.image_label.setStyleSheet("background-color: #f0f0f0; font-size: 14px;")
        layout.addWidget(self.image_label)

        self.status_bar.showMessage("Выберите источник данных...")

        central_widget.setLayout(layout)

    def _select_folder(self) -> None:
        """
        Обрабатывает выбор папки с изображениями.
        Создает итератор и загружает список путей.
        """
        folder: str = QFileDialog.getExistingDirectory(
            self, "Выберите папку с изображениями"
        )
        if not folder:
            return

        try:
            iterator = ImgPathIterator(folder)
            self.image_paths = list(iterator)
            self.current_index = 0
            self.status_bar.showMessage(f"Загружено {len(self.image_paths)} изображений")
            self._show_current_image()
        except (OSError, ValueError) as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить папку:\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "Неизвестная ошибка", str(e))

    def _select_csv(self) -> None:
        """
        Обрабатывает выбор CSV-файла аннотации.
        Создает итератор и загружает список путей.
        """
        csv_file, _ = QFileDialog.getOpenFileName(
            self, "Выберите CSV-файл", "", "CSV Files (*.csv)"
        )
        if not csv_file:
            return

        try:
            iterator = ImgPathIterator(csv_file)
            self.image_paths = list(iterator)
            self.current_index = 0
            self.status_bar.showMessage(f"Загружено {len(self.image_paths)} изображений")
            self._show_current_image()
        except (OSError, ValueError) as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить CSV:\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "Неизвестная ошибка", str(e))

    def _show_current_image(self) -> None:
        """Отображает изображение, соответствующее текущему индексу."""
        if not self.image_paths or self.image_label is None:
            self._show_placeholder("Нет изображений для отображения.")
            return

        path = self.image_paths[self.current_index]
        self.current_image_path = path

        pixmap = QPixmap(path)
        if pixmap.isNull():
            self._show_placeholder(f"❌ Не удалось загрузить: {os.path.basename(path)}")
            return

        # Масштабируем с сохранением пропорций
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setStyleSheet("")  # Убираем фон, чтобы изображение было чётким
        self.status_bar.showMessage(
            f"Изображение {self.current_index + 1} из {len(self.image_paths)}: {os.path.basename(path)}"
        )

    def _show_placeholder(self, text: str) -> None:
        """
        Отображает текст-заглушку вместо изображения.

        Args:
            text (str): Текст для отображения.
        """
        if self.image_label:
            self.image_label.setText(text)
            self.image_label.setPixmap(QPixmap())  # Очищаем изображение
            self.image_label.setStyleSheet("background-color: #e0e0e0; font-size: 14px;")

    def _show_next_image(self) -> None:
        """Переключается на следующее изображение."""
        if not self.image_paths:
            return
        self.current_index = (self.current_index + 1) % len(self.image_paths)
        self._show_current_image()

    def _show_previous_image(self) -> None:
        """Переключается на предыдущее изображение."""
        if not self.image_paths:
            return
        self.current_index = (self.current_index - 1) % len(self.image_paths)
        self._show_current_image()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        Обрабатывает изменение размера окна.
        Перерисовывает изображение, чтобы оно соответствовало новому размеру.

        Args:
            event (QResizeEvent): Событие изменения размера.
        """
        if self.image_paths and self.current_image_path:
            self._show_current_image()
        super().resizeEvent(event)


def main() -> None:
    """
    Точка входа в приложение.
    Инициализирует и запускает Qt-приложение.
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