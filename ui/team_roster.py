# -*- coding: utf-8 -*-

"""
Виджет для отображения и управления составом команды
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QTableWidget, QTableWidgetItem, QHeaderView, 
                           QComboBox, QLabel, QMessageBox, QDialog,
                           QFormLayout, QLineEdit, QDateEdit, QDialogButtonBox,
                           QFileDialog, QSpinBox)
from PyQt5.QtCore import pyqtSignal, Qt, QDate

from models import Player, Team
from services.player_service import PlayerService
from services.team_service import TeamService
from utils import (show_error_message, show_info_message, show_question_message, 
                  format_date, export_to_excel, get_player_photo_path)
from database import get_session

class PlayerDialog(QDialog):
    """Диалог добавления/редактирования игрока"""
    
    def __init__(self, player=None, parent=None):
        super().__init__(parent)
        
        self.player = player
        self.player_service = PlayerService()
        self.team_service = TeamService()
        
        self.init_ui()
        
        if player:
            self.setWindowTitle("Редактирование игрока")
            self.load_player_data()
        else:
            self.setWindowTitle("Добавление игрока")
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QFormLayout(self)
        
        # Фамилия
        self.last_name_edit = QLineEdit()
        layout.addRow("Фамилия:", self.last_name_edit)
        
        # Имя
        self.first_name_edit = QLineEdit()
        layout.addRow("Имя:", self.first_name_edit)
        
        # Отчество
        self.middle_name_edit = QLineEdit()
        layout.addRow("Отчество:", self.middle_name_edit)
        
        # Дата рождения
        self.birth_date_edit = QDateEdit()
        self.birth_date_edit.setCalendarPopup(True)
        self.birth_date_edit.setDate(QDate.currentDate())
        layout.addRow("Дата рождения:", self.birth_date_edit)
        
        # Амплуа
        self.position_combo = QComboBox()
        self.position_combo.addItems(["Нападающий", "Защитник", "Вратарь"])
        layout.addRow("Амплуа:", self.position_combo)
        
        # Номер
        self.jersey_number_spin = QSpinBox()
        self.jersey_number_spin.setMinimum(1)
        self.jersey_number_spin.setMaximum(99)
        layout.addRow("Номер:", self.jersey_number_spin)
        
        # Рост
        self.height_spin = QSpinBox()
        self.height_spin.setMinimum(140)
        self.height_spin.setMaximum(220)
        self.height_spin.setSuffix(" см")
        layout.addRow("Рост:", self.height_spin)
        
        # Вес
        self.weight_spin = QSpinBox()
        self.weight_spin.setMinimum(40)
        self.weight_spin.setMaximum(150)
        self.weight_spin.setSuffix(" кг")
        layout.addRow("Вес:", self.weight_spin)
        
        # Команда
        self.team_combo = QComboBox()
        self.load_teams()
        layout.addRow("Команда:", self.team_combo)
        
        # Фотография
        self.photo_path_edit = QLineEdit()
        self.photo_path_edit.setReadOnly(True)
        
        photo_layout = QHBoxLayout()
        photo_layout.addWidget(self.photo_path_edit)
        
        browse_button = QPushButton("Обзор...")
        browse_button.clicked.connect(self.browse_photo)
        photo_layout.addWidget(browse_button)
        
        layout.addRow("Фотография:", photo_layout)
        
        # Заметки
        self.notes_edit = QLineEdit()
        layout.addRow("Заметки:", self.notes_edit)
        
        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setMinimumWidth(400)
    
    def load_teams(self):
        """Загрузка списка команд в комбобокс"""
        teams = self.team_service.get_all_teams()
        
        self.team_combo.clear()
        for team in teams:
            self.team_combo.addItem(team.name, team.id)
    
    def load_player_data(self):
        """Загрузка данных игрока в поля формы"""
        if not self.player:
            return
        
        self.last_name_edit.setText(self.player.last_name)
        self.first_name_edit.setText(self.player.first_name)
        self.middle_name_edit.setText(self.player.middle_name or "")
        
        if self.player.birth_date:
            self.birth_date_edit.setDate(QDate(
                self.player.birth_date.year,
                self.player.birth_date.month,
                self.player.birth_date.day
            ))
        
        # Установка амплуа
        position_index = self.position_combo.findText(self.player.position)
        if position_index >= 0:
            self.position_combo.setCurrentIndex(position_index)
        
        # Установка номера
        if self.player.jersey_number:
            self.jersey_number_spin.setValue(self.player.jersey_number)
        
        # Установка роста
        if self.player.height:
            self.height_spin.setValue(self.player.height)
        
        # Установка веса
        if self.player.weight:
            self.weight_spin.setValue(self.player.weight)
        
        # Установка команды
        if self.player.team_id:
            team_index = self.team_combo.findData(self.player.team_id)
            if team_index >= 0:
                self.team_combo.setCurrentIndex(team_index)
        
        # Установка пути к фотографии
        if self.player.photo_path:
            self.photo_path_edit.setText(self.player.photo_path)
        
        # Установка заметок
        if self.player.notes:
            self.notes_edit.setText(self.player.notes)
    
    def browse_photo(self):
        """Открытие диалога выбора фотографии"""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выбор фотографии игрока",
            "",
            "Изображения (*.jpg *.jpeg *.png)",
            options=options
        )
        
        if file_path:
            self.photo_path_edit.setText(file_path)
    
    def get_player_data(self):
        """Получение данных игрока из формы"""
        player_data = {
            'last_name': self.last_name_edit.text().strip(),
            'first_name': self.first_name_edit.text().strip(),
            'middle_name': self.middle_name_edit.text().strip() or None,
            'birth_date': self.birth_date_edit.date().toPyDate(),
            'position': self.position_combo.currentText(),
            'jersey_number': self.jersey_number_spin.value(),
            'height': self.height_spin.value(),
            'weight': self.weight_spin.value(),
            'team_id': self.team_combo.currentData(),
            'photo_path': self.photo_path_edit.text() or None,
            'notes': self.notes_edit.text().strip() or None
        }
        
        return player_data
    
    def accept(self):
        """Обработка нажатия кнопки OK"""
        player_data = self.get_player_data()
        
        # Проверка обязательных полей
        if not player_data['last_name'] or not player_data['first_name']:
            show_error_message(self, "Ошибка", "Фамилия и имя обязательны для заполнения")
            return
        
        try:
            if self.player:
                # Обновление игрока
                self.player_service.update_player(self.player.id, player_data)
            else:
                # Создание нового игрока
                self.player_service.create_player(player_data)
            
            super().accept()
        except Exception as e:
            show_error_message(self, "Ошибка", f"Не удалось сохранить данные игрока: {str(e)}")

class TeamRosterWidget(QWidget):
    """Виджет для отображения и управления составом команды"""
    
    # Сигнал о выборе игрока
    player_selected = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        
        self.player_service = PlayerService()
        self.team_service = TeamService()
        
        self.init_ui()
        self.load_players()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout(self)
        
        # Панель фильтров
        filter_layout = QHBoxLayout()
        
        # Фильтр по команде
        filter_layout.addWidget(QLabel("Команда:"))
        self.team_filter = QComboBox()
        self.team_filter.currentIndexChanged.connect(self.load_players)
        filter_layout.addWidget(self.team_filter)
        
        # Фильтр по амплуа
        filter_layout.addWidget(QLabel("Амплуа:"))
        self.position_filter = QComboBox()
        self.position_filter.addItem("Все", "")
        self.position_filter.addItem("Нападающие", "Нападающий")
        self.position_filter.addItem("Защитники", "Защитник")
        self.position_filter.addItem("Вратари", "Вратарь")
        self.position_filter.currentIndexChanged.connect(self.load_players)
        filter_layout.addWidget(self.position_filter)
        
        filter_layout.addStretch()
        
        # Кнопки действий
        add_button = QPushButton("Добавить игрока")
        add_button.clicked.connect(self.add_player)
        filter_layout.addWidget(add_button)
        
        edit_button = QPushButton("Редактировать")
        edit_button.clicked.connect(self.edit_player)
        filter_layout.addWidget(edit_button)
        
        delete_button = QPushButton("Удалить")
        delete_button.clicked.connect(self.delete_player)
        filter_layout.addWidget(delete_button)
        
        layout.addLayout(filter_layout)
        
        # Таблица игроков
        self.players_table = QTableWidget()
        self.players_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.players_table.setSelectionMode(QTableWidget.SingleSelection)
        self.players_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.players_table.setColumnCount(8)
        self.players_table.setHorizontalHeaderLabels([
            "ID", "Фамилия", "Имя", "Отчество", "Дата рождения", "Амплуа", "Команда", "Номер"
        ])
        
        # Настройка ширины колонок
        self.players_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.players_table.setColumnHidden(0, True)  # Скрываем ID
        
        # Подключение сигнала выбора строки
        self.players_table.itemSelectionChanged.connect(self.on_player_selected)
        
        layout.addWidget(self.players_table)
        
        # Загрузка команд
        self.load_teams()
    
    def load_teams(self):
        """Загрузка списка команд в фильтр"""
        teams = self.team_service.get_all_teams()
        
        self.team_filter.clear()
        self.team_filter.addItem("Все команды", None)
        
        for team in teams:
            self.team_filter.addItem(team.name, team.id)
    
    def load_players(self):
        """Загрузка списка игроков с учетом фильтров"""
        team_id = self.team_filter.currentData()
        position = self.position_filter.currentData()
        
        players = self.player_service.get_players(team_id, position)
        
        self.players_table.setRowCount(0)
        for row, player in enumerate(players):
            self.players_table.insertRow(row)
            
            # Заполнение ячеек
            self.players_table.setItem(row, 0, QTableWidgetItem(str(player.id)))
            self.players_table.setItem(row, 1, QTableWidgetItem(player.last_name))
            self.players_table.setItem(row, 2, QTableWidgetItem(player.first_name))
            self.players_table.setItem(row, 3, QTableWidgetItem(player.middle_name or ""))
            
            birth_date = format_date(player.birth_date) if player.birth_date else ""
            self.players_table.setItem(row, 4, QTableWidgetItem(birth_date))
            
            self.players_table.setItem(row, 5, QTableWidgetItem(player.position))
            
            team_name = player.team.name if player.team else ""
            self.players_table.setItem(row, 6, QTableWidgetItem(team_name))
            
            jersey_number = str(player.jersey_number) if player.jersey_number else ""
            self.players_table.setItem(row, 7, QTableWidgetItem(jersey_number))
    
    def add_player(self):
        """Добавление нового игрока"""
        dialog = PlayerDialog(parent=self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            self.load_players()
            show_info_message(self, "Информация", "Игрок успешно добавлен")
    
    def edit_player(self):
        """Редактирование выбранного игрока"""
        # Получение выбранного игрока
        selected_rows = self.players_table.selectedItems()
        if not selected_rows:
            show_error_message(self, "Ошибка", "Необходимо выбрать игрока для редактирования")
            return
        
        # Получение ID игрока
        player_id = int(self.players_table.item(selected_rows[0].row(), 0).text())
        
        # Получение данных игрока
        player = self.player_service.get_player_by_id(player_id)
        if not player:
            show_error_message(self, "Ошибка", "Игрок не найден")
            return
        
        # Открытие диалога редактирования
        dialog = PlayerDialog(player, parent=self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            self.load_players()
            show_info_message(self, "Информация", "Данные игрока успешно обновлены")
    
    def delete_player(self):
        """Удаление выбранного игрока"""
        # Получение выбранного игрока
        selected_rows = self.players_table.selectedItems()
        if not selected_rows:
            show_error_message(self, "Ошибка", "Необходимо выбрать игрока для удаления")
            return
        
        # Получение ID игрока
        player_id = int(self.players_table.item(selected_rows[0].row(), 0).text())
        
        # Подтверждение удаления
        if not show_question_message(self, "Подтверждение", "Вы действительно хотите удалить выбранного игрока?"):
            return
        
        # Удаление игрока
        try:
            self.player_service.delete_player(player_id)
            self.load_players()
            show_info_message(self, "Информация", "Игрок успешно удален")
        except Exception as e:
            show_error_message(self, "Ошибка", f"Не удалось удалить игрока: {str(e)}")
    
    def on_player_selected(self):
        """Обработчик выбора игрока в таблице"""
        selected_rows = self.players_table.selectedItems()
        if not selected_rows:
            return
        
        # Получение ID игрока
        player_id = int(self.players_table.item(selected_rows[0].row(), 0).text())
        
        # Получение данных игрока
        player = self.player_service.get_player_by_id(player_id)
        if player:
            # Отправка сигнала с выбранным игроком
            self.player_selected.emit(player)
    
    def export_to_excel(self):
        """Экспорт списка игроков в Excel"""
        try:
            # Получаем данные из таблицы
            data = []
            headers = ["Фамилия", "Имя", "Отчество", "Дата рождения", "Амплуа", "Команда", "Номер"]
            
            for row in range(self.players_table.rowCount()):
                row_data = {}
                for col in range(1, self.players_table.columnCount()):  # Пропускаем колонку ID
                    row_data[headers[col-1]] = self.players_table.item(row, col).text()
                data.append(row_data)
            
            # Экспорт в Excel
            filepath = export_to_excel(data, "Состав_команды.xlsx", "Игроки")
            show_info_message(self, "Экспорт", f"Данные успешно экспортированы в файл:\n{filepath}")
        except Exception as e:
            show_error_message(self, "Ошибка", f"Не удалось экспортировать данные: {str(e)}")
