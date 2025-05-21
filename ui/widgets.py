# -*- coding: utf-8 -*-

"""
Вспомогательные виджеты для интерфейса
"""

from PyQt5.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QComboBox, QLineEdit, QDateEdit, QMessageBox,
                           QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QColor

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import pandas as pd

from utils import date_to_qdate, format_date, show_error_message, show_info_message


class PlayerPhotoWidget(QWidget):
    """Виджет для отображения фото игрока"""
    
    photo_changed = pyqtSignal(str)
    
    def __init__(self, photo_path=None, editable=True, parent=None):
        super().__init__(parent)
        
        self.photo_path = photo_path
        self.editable = editable
        
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Виджет фото
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(200, 200)
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.photo_label.setStyleSheet("background-color: lightgray; border: 1px solid gray;")
        
        layout.addWidget(self.photo_label)
        
        # Кнопка изменения фото
        if self.editable:
            self.change_button = QPushButton("Изменить фото")
            self.change_button.clicked.connect(self.change_photo)
            layout.addWidget(self.change_button)
        
        # Установка фото
        self.set_photo(self.photo_path)
    
    def set_photo(self, photo_path):
        """Установка фотографии"""
        self.photo_path = photo_path
        
        if not photo_path:
            self.photo_label.setText("Нет фото")
            self.photo_label.setPixmap(QPixmap())
            return
        
        pixmap = QPixmap(photo_path)
        if pixmap.isNull():
            self.photo_label.setText("Ошибка загрузки фото")
            return
        
        # Масштабирование фото
        pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.photo_label.setPixmap(pixmap)
        self.photo_label.setText("")
    
    def change_photo(self):
        """Изменение фотографии"""
        from PyQt5.QtWidgets import QFileDialog
        
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выбор фотографии",
            "",
            "Изображения (*.jpg *.jpeg *.png)",
            options=options
        )
        
        if file_path:
            self.set_photo(file_path)
            self.photo_changed.emit(file_path)


class StatisticsChart(QWidget):
    """Виджет для отображения графиков статистики"""
    
    def __init__(self, title="", xlabel="", ylabel="", parent=None):
        super().__init__(parent)
        
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Заголовок
        self.title_label = QLabel(self.title)
        title_font = QFont()
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Виджет для графика
        self.chart_widget = QWidget()
        self.chart_layout = QVBoxLayout(self.chart_widget)
        self.chart_layout.setContentsMargins(0, 0, 0, 0)
        
        # Начальное сообщение
        self.message_label = QLabel("Нет данных для отображения")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.chart_layout.addWidget(self.message_label)
        
        layout.addWidget(self.chart_widget)
    
    def plot_bar_chart(self, data, labels):
        """Построение столбчатой диаграммы"""
        # Очистка виджета
        self._clear_chart()
        
        if not data or not labels:
            self.message_label.setText("Нет данных для отображения")
            self.chart_layout.addWidget(self.message_label)
            return
        
        # Создание фигуры и осей
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        # Построение диаграммы
        ax.bar(labels, data)
        
        # Настройка графика
        ax.set_title(self.title)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        
        # Поворот подписей по оси X, если их много
        if len(labels) > 5:
            for label in ax.get_xticklabels():
                label.set_rotation(45)
                label.set_ha('right')
        
        fig.tight_layout()
        
        # Создание холста
        canvas = FigureCanvas(fig)
        self.chart_layout.addWidget(canvas)
    
    def plot_line_chart(self, data, labels):
        """Построение линейного графика"""
        # Очистка виджета
        self._clear_chart()
        
        if not data or not labels:
            self.message_label.setText("Нет данных для отображения")
            self.chart_layout.addWidget(self.message_label)
            return
        
        # Создание фигуры и осей
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        # Построение графика
        ax.plot(labels, data, marker='o')
        
        # Настройка графика
        ax.set_title(self.title)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        
        # Поворот подписей по оси X, если их много
        if len(labels) > 5:
            for label in ax.get_xticklabels():
                label.set_rotation(45)
                label.set_ha('right')
        
        fig.tight_layout()
        
        # Создание холста
        canvas = FigureCanvas(fig)
        self.chart_layout.addWidget(canvas)
    
    def plot_pie_chart(self, data, labels):
        """Построение круговой диаграммы"""
        # Очистка виджета
        self._clear_chart()
        
        if not data or not labels:
            self.message_label.setText("Нет данных для отображения")
            self.chart_layout.addWidget(self.message_label)
            return
        
        # Создание фигуры и осей
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        # Построение диаграммы
        ax.pie(data, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Равные оси для правильного отображения круга
        
        # Настройка графика
        ax.set_title(self.title)
        
        fig.tight_layout()
        
        # Создание холста
        canvas = FigureCanvas(fig)
        self.chart_layout.addWidget(canvas)
    
    def _clear_chart(self):
        """Очистка виджета графика"""
        # Удаление всех виджетов из layout
        while self.chart_layout.count():
            item = self.chart_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()


class DateRangeSelector(QWidget):
    """Виджет для выбора диапазона дат"""
    
    date_range_changed = pyqtSignal(object, object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Метка
        layout.addWidget(QLabel("Период:"))
        
        # Виджет выбора начальной даты
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))
        layout.addWidget(self.start_date_edit)
        
        # Разделитель
        layout.addWidget(QLabel("-"))
        
        # Виджет выбора конечной даты
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate().addDays(30))
        layout.addWidget(self.end_date_edit)
        
        # Кнопка применения
        self.apply_button = QPushButton("Применить")
        self.apply_button.clicked.connect(self.on_apply)
        layout.addWidget(self.apply_button)
        
        # Предустановленные периоды
        self.period_combo = QComboBox()
        self.period_combo.addItem("Пользовательский")
        self.period_combo.addItem("Сегодня")
        self.period_combo.addItem("Вчера")
        self.period_combo.addItem("Неделя")
        self.period_combo.addItem("Месяц")
        self.period_combo.addItem("Год")
        self.period_combo.currentIndexChanged.connect(self.on_period_selected)
        layout.addWidget(self.period_combo)
        
        # Подключение сигналов изменения дат
        self.start_date_edit.dateChanged.connect(self.on_date_changed)
        self.end_date_edit.dateChanged.connect(self.on_date_changed)
    
    def set_date_range(self, start_date, end_date):
        """Установка диапазона дат"""
        self.start_date_edit.setDate(date_to_qdate(start_date))
        self.end_date_edit.setDate(date_to_qdate(end_date))
    
    def get_date_range(self):
        """Получение диапазона дат"""
        start_date = self.start_date_edit.date().toPyDate()
        end_date = self.end_date_edit.date().toPyDate()
        return start_date, end_date
    
    def on_date_changed(self):
        """Обработчик изменения даты"""
        # Установка индекса комбобокса в "Пользовательский"
        self.period_combo.setCurrentIndex(0)
    
    def on_period_selected(self, index):
        """Обработчик выбора предустановленного периода"""
        if index == 0:  # Пользовательский
            return
        
        today = QDate.currentDate()
        
        if index == 1:  # Сегодня
            self.start_date_edit.setDate(today)
            self.end_date_edit.setDate(today)
        elif index == 2:  # Вчера
            yesterday = today.addDays(-1)
            self.start_date_edit.setDate(yesterday)
            self.end_date_edit.setDate(yesterday)
        elif index == 3:  # Неделя
            self.start_date_edit.setDate(today.addDays(-7))
            self.end_date_edit.setDate(today)
        elif index == 4:  # Месяц
            self.start_date_edit.setDate(today.addMonths(-1))
            self.end_date_edit.setDate(today)
        elif index == 5:  # Год
            self.start_date_edit.setDate(today.addYears(-1))
            self.end_date_edit.setDate(today)
    
    def on_apply(self):
        """Обработчик нажатия кнопки применения"""
        start_date, end_date = self.get_date_range()
        
        # Проверка корректности дат
        if start_date > end_date:
            show_error_message(self, "Ошибка", "Дата начала не может быть позже даты окончания")
            return
        
        self.date_range_changed.emit(start_date, end_date)


class SearchWidget(QWidget):
    """Виджет для поиска"""
    
    search_changed = pyqtSignal(str)
    
    def __init__(self, placeholder="Поиск...", parent=None):
        super().__init__(parent)
        
        self.placeholder = placeholder
        
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Поле поиска
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(self.placeholder)
        self.search_edit.textChanged.connect(self.on_search_changed)
        layout.addWidget(self.search_edit)
        
        # Кнопка очистки
        self.clear_button = QPushButton("✕")
        self.clear_button.setFixedWidth(30)
        self.clear_button.clicked.connect(self.clear_search)
        layout.addWidget(self.clear_button)
    
    def on_search_changed(self, text):
        """Обработчик изменения текста поиска"""
        self.search_changed.emit(text)
    
    def clear_search(self):
        """Очистка поля поиска"""
        self.search_edit.clear()
    
    def get_search_text(self):
        """Получение текста поиска"""
        return self.search_edit.text()


class FilterComboBox(QWidget):
    """Виджет комбобокса с фильтром"""
    
    selection_changed = pyqtSignal(object)
    
    def __init__(self, label="", parent=None):
        super().__init__(parent)
        
        self.label_text = label
        
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Метка
        if self.label_text:
            self.label = QLabel(self.label_text)
            layout.addWidget(self.label)
        
        # Комбобокс
        self.combo = QComboBox()
        self.combo.currentIndexChanged.connect(self.on_selection_changed)
        layout.addWidget(self.combo)
    
    def add_item(self, text, data=None):
        """Добавление элемента в комбобокс"""
        self.combo.addItem(text, data)
    
    def add_items(self, items):
        """Добавление нескольких элементов"""
        for text, data in items:
            self.add_item(text, data)
    
    def clear(self):
        """Очистка комбобокса"""
        self.combo.clear()
    
    def set_current_index(self, index):
        """Установка текущего индекса"""
        self.combo.setCurrentIndex(index)
    
    def set_current_data(self, data):
        """Установка текущего элемента по данным"""
        index = self.combo.findData(data)
        if index >= 0:
            self.combo.setCurrentIndex(index)
    
    def get_current_data(self):
        """Получение данных текущего элемента"""
        return self.combo.currentData()
    
    def get_current_text(self):
        """Получение текста текущего элемента"""
        return self.combo.currentText()
    
    def on_selection_changed(self, index):
        """Обработчик изменения выбора"""
        self.selection_changed.emit(self.combo.currentData())


class PlayerStatsCompareWidget(QWidget):
    """Виджет для сравнения статистики игроков"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout(self)
        
        # Заголовок
        title = QLabel("Сравнение статистики игроков")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Таблица сравнения
        self.compare_table = QTableWidget()
        self.compare_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.compare_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.compare_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.compare_table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.compare_table)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        self.add_player_button = QPushButton("Добавить игрока")
        buttons_layout.addWidget(self.add_player_button)
        
        self.remove_player_button = QPushButton("Удалить")
        buttons_layout.addWidget(self.remove_player_button)
        
        buttons_layout.addStretch()
        
        self.show_chart_button = QPushButton("Показать график")
        buttons_layout.addWidget(self.show_chart_button)
        
        layout.addLayout(buttons_layout)
        
        # График
        self.chart = StatisticsChart(
            title="Сравнение показателей",
            xlabel="Игроки",
            ylabel="Значение"
        )
        layout.addWidget(self.chart)
    
    def set_players(self, players_stats):
        """Установка данных игроков для сравнения"""
        if not players_stats:
            self.compare_table.setRowCount(0)
            self.compare_table.setColumnCount(0)
            return
        
        # Настройка таблицы
        num_players = len(players_stats)
        self.compare_table.setColumnCount(num_players + 1)  # +1 для названий показателей
        
        # Установка заголовков колонок (имена игроков)
        headers = ["Показатель"]
        for i, stats in enumerate(players_stats):
            headers.append(stats.get('name', f"Игрок {i+1}"))
        
        self.compare_table.setHorizontalHeaderLabels(headers)
        
        # Определяем показатели для сравнения
        metrics = [
            "Матчи", "Голы", "Передачи", "Очки", "+/-", 
            "Штраф. мин.", "Броски", "% вбрасываний"
        ]
        
        self.compare_table.setRowCount(len(metrics))
        
        # Заполнение таблицы
        for row, metric in enumerate(metrics):
            # Название показателя
            self.compare_table.setItem(row, 0, QTableWidgetItem(metric))
            
            # Значения для каждого игрока
            for col, stats in enumerate(players_stats):
                value = ""
                
                if metric == "Матчи":
                    value = str(stats.get('games', 0))
                elif metric == "Голы":
                    value = str(stats.get('goals', 0))
                elif metric == "Передачи":
                    value = str(stats.get('assists', 0))
                elif metric == "Очки":
                    value = str(stats.get('points', 0))
                elif metric == "+/-":
                    value = str(stats.get('plus_minus', 0))
                elif metric == "Штраф. мин.":
                    value = str(stats.get('penalty_minutes', 0))
                elif metric == "Броски":
                    value = str(stats.get('shots', 0))
                elif metric == "% вбрасываний":
                    value = f"{stats.get('faceoff_percentage', 0):.1f}%"
                
                item = QTableWidgetItem(value)
                
                # Устанавливаем выравнивание по центру
                item.setTextAlignment(Qt.AlignCenter)
                
                self.compare_table.setItem(row, col + 1, item)
        
        # Подсветка лучших значений
        self._highlight_best_values()
    
    def show_chart_for_metric(self, metric_index):
        """Показать график для выбранного показателя"""
        if metric_index < 0 or metric_index >= self.compare_table.rowCount():
            return
        
        # Получение названия показателя
        metric_name = self.compare_table.item(metric_index, 0).text()
        
        # Получение данных игроков и их значений
        player_names = []
        values = []
        
        for col in range(1, self.compare_table.columnCount()):
            player_names.append(self.compare_table.horizontalHeaderItem(col).text())
            
            value_item = self.compare_table.item(metric_index, col)
            if value_item:
                # Обработка процентов и других форматов
                value_text = value_item.text()
                try:
                    # Удаление символа % и преобразование в число
                    if "%" in value_text:
                        value = float(value_text.replace("%", ""))
                    else:
                        value = float(value_text)
                    values.append(value)
                except ValueError:
                    values.append(0)
            else:
                values.append(0)
        
        # Обновление заголовков графика
        self.chart.title = f"Сравнение: {metric_name}"
        self.chart.ylabel = metric_name
        self.chart.title_label.setText(self.chart.title)
        
        # Отображение графика
        self.chart.plot_bar_chart(values, player_names)
    
    def _highlight_best_values(self):
        """Подсветка лучших значений в таблице"""
        for row in range(self.compare_table.rowCount()):
            metric = self.compare_table.item(row, 0).text()
            
            # Определяем, является ли большее значение лучшим для этого показателя
            higher_is_better = True
            if metric == "Штраф. мин.":
                higher_is_better = False
            
            # Находим лучшее значение
            best_value = None
            best_col = None
            
            for col in range(1, self.compare_table.columnCount()):
                item = self.compare_table.item(row, col)
                if not item:
                    continue
                
                value_text = item.text()
                
                try:
                    # Обработка процентов и других форматов
                    if "%" in value_text:
                        value = float(value_text.replace("%", ""))
                    else:
                        value = float(value_text)
                    
                    if best_value is None or (higher_is_better and value > best_value) or (not higher_is_better and value < best_value):
                        best_value = value
                        best_col = col
                except ValueError:
                    continue
            
            # Подсветка лучшего значения
            if best_col is not None:
                item = self.compare_table.item(row, best_col)
                item.setBackground(QColor(200, 255, 200))  # Светло-зеленый цвет

