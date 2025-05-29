# -*- coding: utf-8 -*-

"""
Виджет для отображения и управления расписанием матчей
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                          QTableWidget, QTableWidgetItem, QHeaderView, QCalendarWidget,
                          QDateEdit, QTimeEdit, QMessageBox, QDialog, QFormLayout,
                          QLineEdit, QComboBox, QDialogButtonBox, QGroupBox, QSpinBox)
from PyQt5.QtCore import QDate, QTime, Qt, pyqtSignal

from models import Match
from services.match_service import MatchService
from services.team_service import TeamService
from services.stats_service import StatsService
from ui.dialogs import MatchDialog, MatchResultsDialog
from utils import (format_date, format_time, export_to_excel, date_to_qdate, time_to_qtime,
                qdate_to_date, qtime_to_time, show_error_message, show_info_message,
                show_question_message)
import datetime

class MatchScheduleWidget(QWidget):
    """Виджет для отображения и управления расписанием матчей"""
    
    def __init__(self):
        super().__init__()
        
        self.match_service = MatchService()
        self.team_service = TeamService()
        self.stats_service = StatsService()
        
        self.init_ui()
        self.load_teams()
        self.load_matches()  # Загружаем матчи при инициализации
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout(self)
        
        # Панель фильтров и элементов управления
        control_layout = QHBoxLayout()
        
        # Календарь для выбора даты
        self.calendar = QCalendarWidget()
        self.calendar.setMaximumWidth(350)
        self.calendar.setMaximumHeight(350)
        self.calendar.selectionChanged.connect(self.on_date_selected)
        control_layout.addWidget(self.calendar, 1)
        
        # Группа фильтров и действий
        filters_group = QGroupBox("Фильтры и действия")
        filters_layout = QFormLayout(filters_group)
        
        # Выбор команды
        filters_layout.addRow(QLabel("Команда:"))
        self.team_combo = QComboBox()
        self.team_combo.currentIndexChanged.connect(self.load_matches)
        filters_layout.addRow(self.team_combo)
        
        # Статус матча
        filters_layout.addRow(QLabel("Статус:"))
        self.status_combo = QComboBox()
        self.status_combo.addItem("Все", None)
        self.status_combo.addItem("Запланирован", "запланирован")
        self.status_combo.addItem("Завершен", "завершен")
        self.status_combo.addItem("Отменен", "отменен")
        self.status_combo.currentIndexChanged.connect(self.load_matches)
        filters_layout.addRow(self.status_combo)
        
        # Диапазон дат
        filters_layout.addRow(QLabel("Период:"))
        dates_layout = QHBoxLayout()
        
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))
        dates_layout.addWidget(self.start_date_edit)
        
        dates_layout.addWidget(QLabel(" - "))
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate().addDays(30))
        dates_layout.addWidget(self.end_date_edit)
        
        filters_layout.addRow(dates_layout)
        
        # Кнопка применения фильтров
        apply_button = QPushButton("Применить фильтры")
        apply_button.clicked.connect(self.load_matches)
        filters_layout.addRow(apply_button)
        
        # Разделитель
        filters_layout.addRow(QLabel(""))
        
        # Кнопки действий
        actions_layout = QVBoxLayout()
        
        add_button = QPushButton("Добавить матч")
        add_button.clicked.connect(self.add_match)
        actions_layout.addWidget(add_button)
        
        edit_button = QPushButton("Редактировать")
        edit_button.clicked.connect(self.edit_match)
        actions_layout.addWidget(edit_button)
        
        delete_button = QPushButton("Удалить")
        delete_button.clicked.connect(self.delete_match)
        actions_layout.addWidget(delete_button)
        
        results_button = QPushButton("Внести результаты")
        results_button.clicked.connect(self.update_match_results)
        actions_layout.addWidget(results_button)
        
        export_button = QPushButton("Экспорт в Excel")
        export_button.clicked.connect(self.export_to_excel)
        actions_layout.addWidget(export_button)
        
        filters_layout.addRow(actions_layout)
        
        control_layout.addWidget(filters_group, 1)
        
        layout.addLayout(control_layout)
        
        # Таблица матчей
        self.matches_table = QTableWidget()
        self.matches_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.matches_table.setSelectionMode(QTableWidget.SingleSelection)
        self.matches_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.matches_table.setColumnCount(8)
        self.matches_table.setHorizontalHeaderLabels([
            "ID", "Дата", "Время", "Хозяева", "Гости", "Счет", "Место", "Статус"
        ])
        self.matches_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.matches_table.setColumnHidden(0, True)  # Скрываем ID
        self.matches_table.doubleClicked.connect(self.edit_match)
        
        layout.addWidget(QLabel("Расписание матчей:"))
        layout.addWidget(self.matches_table)
    
    def load_teams(self):
        """Загрузка списка команд"""
        teams = self.team_service.get_all_teams()
        
        self.team_combo.clear()
        self.team_combo.addItem("Все команды", None)
        
        for team in teams:
            self.team_combo.addItem(team.name, team.id)
    
    def load_matches(self):
        """Загрузка списка матчей с учетом фильтров"""
        try:
            team_id = self.team_combo.currentData()
            status = self.status_combo.currentData()
            start_date = self.start_date_edit.date().toPyDate()
            end_date = self.end_date_edit.date().toPyDate()
            
            matches = self.match_service.get_matches(team_id, status, start_date, end_date)
        except Exception as e:
            print(f"Ошибка при загрузке матчей: {str(e)}")
            matches = []
        
        self.matches_table.setRowCount(0)
        for row, match in enumerate(matches):
            self.matches_table.insertRow(row)
            
            self.matches_table.setItem(row, 0, QTableWidgetItem(str(match.id)))
            self.matches_table.setItem(row, 1, QTableWidgetItem(format_date(match.date)))
            
            time_str = format_time(match.time) if match.time else ""
            self.matches_table.setItem(row, 2, QTableWidgetItem(time_str))
            
            home_team = match.home_team.name if match.home_team else ""
            self.matches_table.setItem(row, 3, QTableWidgetItem(home_team))
            
            away_team = match.away_team.name if match.away_team else ""
            self.matches_table.setItem(row, 4, QTableWidgetItem(away_team))
            
            # Счет
            score = ""
            if match.home_score is not None and match.away_score is not None:
                score = f"{match.home_score} - {match.away_score}"
            self.matches_table.setItem(row, 5, QTableWidgetItem(score))
            
            self.matches_table.setItem(row, 6, QTableWidgetItem(match.location or ""))
            self.matches_table.setItem(row, 7, QTableWidgetItem(match.status or ""))
            
            # Выделение прошедших и будущих матчей разным цветом
            if match.status == "завершен":
                for col in range(1, self.matches_table.columnCount()):
                    item = self.matches_table.item(row, col)
                    if item:
                        item.setBackground(Qt.green)
            elif match.status == "отменен":
                for col in range(1, self.matches_table.columnCount()):
                    item = self.matches_table.item(row, col)
                    if item:
                        item.setBackground(Qt.red)
        
        # Выделение цветом матчей текущего дня
        current_date = QDate.currentDate().toPyDate()
        for row in range(self.matches_table.rowCount()):
            date_str = self.matches_table.item(row, 1).text()
            try:
                parts = date_str.split('.')
                if len(parts) == 3:
                    day, month, year = map(int, parts)
                    match_date = datetime.date(year, month, day)
                    if match_date == current_date and self.matches_table.item(row, 7).text() == "запланирован":
                        for col in range(1, self.matches_table.columnCount()):
                            item = self.matches_table.item(row, col)
                            if item:
                                item.setBackground(Qt.yellow)
            except:
                pass
    
    def on_date_selected(self):
        """Обработчик выбора даты в календаре"""
        selected_date = self.calendar.selectedDate()
        
        # Обновляем диапазон дат
        self.start_date_edit.setDate(selected_date)
        self.end_date_edit.setDate(selected_date)
        
        # Загружаем матчи на выбранную дату
        self.load_matches()
    
    def add_match(self):
        """Добавление нового матча"""
        dialog = MatchDialog(parent=self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            self.load_matches()
            show_info_message(self, "Информация", "Матч успешно добавлен")
    
    def edit_match(self):
        """Редактирование выбранного матча"""
        selected_rows = self.matches_table.selectedItems()
        if not selected_rows:
            show_error_message(self, "Ошибка", "Необходимо выбрать матч для редактирования")
            return
        
        match_id = int(self.matches_table.item(selected_rows[0].row(), 0).text())
        match = self.match_service.get_match_by_id(match_id)
        
        if not match:
            show_error_message(self, "Ошибка", "Матч не найден")
            return
        
        dialog = MatchDialog(match, parent=self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            self.load_matches()
            show_info_message(self, "Информация", "Матч успешно обновлен")
    
    def delete_match(self):
        """Удаление выбранного матча"""
        selected_rows = self.matches_table.selectedItems()
        if not selected_rows:
            show_error_message(self, "Ошибка", "Необходимо выбрать матч для удаления")
            return
        
        match_id = int(self.matches_table.item(selected_rows[0].row(), 0).text())
        
        if not show_question_message(self, "Подтверждение", "Вы действительно хотите удалить выбранный матч?"):
            return
        
        try:
            self.match_service.delete_match(match_id)
            self.load_matches()
            show_info_message(self, "Информация", "Матч успешно удален")
        except Exception as e:
            show_error_message(self, "Ошибка", f"Не удалось удалить матч: {str(e)}")
    
    def update_match_results(self):
        """Внесение результатов матча"""
        selected_rows = self.matches_table.selectedItems()
        if not selected_rows:
            show_error_message(self, "Ошибка", "Необходимо выбрать матч для внесения результатов")
            return
        
        match_id = int(self.matches_table.item(selected_rows[0].row(), 0).text())
        match = self.match_service.get_match_by_id(match_id)
        
        if not match:
            show_error_message(self, "Ошибка", "Матч не найден")
            return
        
        if match.status == "отменен":
            show_error_message(self, "Ошибка", "Нельзя внести результаты отмененного матча")
            return
        
        dialog = MatchResultsDialog(match, parent=self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            self.load_matches()
            show_info_message(self, "Информация", "Результаты матча успешно обновлены")
    
    def export_to_excel(self):
        """Экспорт расписания матчей в Excel"""
        try:
            # Получаем данные из таблицы
            data = []
            headers = ["Дата", "Время", "Хозяева", "Гости", "Счет", "Место", "Статус"]
            
            for row in range(self.matches_table.rowCount()):
                row_data = {}
                for col in range(1, self.matches_table.columnCount()):
                    row_data[headers[col-1]] = self.matches_table.item(row, col).text()
                data.append(row_data)
            
            # Экспорт в Excel
            filepath = export_to_excel(data, "Расписание_матчей.xlsx", "Матчи")
            show_info_message(self, "Экспорт", f"Данные успешно экспортированы в файл:\n{filepath}")
        except Exception as e:
            show_error_message(self, "Ошибка", f"Не удалось экспортировать данные: {str(e)}")

