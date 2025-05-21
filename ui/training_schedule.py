# -*- coding: utf-8 -*-

"""
Виджет для отображения и управления расписанием тренировок
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                          QTableWidget, QTableWidgetItem, QHeaderView, QCalendarWidget,
                          QDateEdit, QTimeEdit, QMessageBox, QDialog, QFormLayout,
                          QLineEdit, QComboBox, QDialogButtonBox, QCheckBox, QGroupBox,
                          QGridLayout)
from PyQt5.QtCore import QDate, QTime, Qt, pyqtSignal

from models import Training, Attendance
from services.training_service import TrainingService
from services.team_service import TeamService
from services.player_service import PlayerService
from ui.dialogs import AttendanceDialog, TrainingDialog
from utils import (format_date, format_time, export_to_excel, date_to_qdate, time_to_qtime,
                 qdate_to_date, qtime_to_time, show_error_message, show_info_message,
                 show_question_message)

class TrainingScheduleWidget(QWidget):
    """Виджет для отображения и управления расписанием тренировок"""
    
    def __init__(self):
        super().__init__()
        
        self.training_service = TrainingService()
        self.team_service = TeamService()
        
        self.init_ui()
        self.load_teams()
    
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
        self.team_combo.currentIndexChanged.connect(self.load_trainings)
        filters_layout.addRow(self.team_combo)
        
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
        apply_button.clicked.connect(self.load_trainings)
        filters_layout.addRow(apply_button)
        
        # Разделитель
        filters_layout.addRow(QLabel(""))
        
        # Кнопки действий
        actions_layout = QVBoxLayout()
        
        add_button = QPushButton("Добавить тренировку")
        add_button.clicked.connect(self.add_training)
        actions_layout.addWidget(add_button)
        
        edit_button = QPushButton("Редактировать")
        edit_button.clicked.connect(self.edit_training)
        actions_layout.addWidget(edit_button)
        
        delete_button = QPushButton("Удалить")
        delete_button.clicked.connect(self.delete_training)
        actions_layout.addWidget(delete_button)
        
        mark_attendance_button = QPushButton("Отметить посещаемость")
        mark_attendance_button.clicked.connect(self.mark_attendance)
        actions_layout.addWidget(mark_attendance_button)
        
        export_button = QPushButton("Экспорт в Excel")
        export_button.clicked.connect(self.export_to_excel)
        actions_layout.addWidget(export_button)
        
        filters_layout.addRow(actions_layout)
        
        control_layout.addWidget(filters_group, 1)
        
        layout.addLayout(control_layout)
        
        # Таблица тренировок
        self.trainings_table = QTableWidget()
        self.trainings_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.trainings_table.setSelectionMode(QTableWidget.SingleSelection)
        self.trainings_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.trainings_table.setColumnCount(8)
        self.trainings_table.setHorizontalHeaderLabels([
            "ID", "Дата", "Время", "Продолжительность", "Команда", "Место", "Направление", "Посещаемость"
        ])
        self.trainings_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.trainings_table.setColumnHidden(0, True)  # Скрываем ID
        self.trainings_table.doubleClicked.connect(self.edit_training)
        
        layout.addWidget(QLabel("Расписание тренировок:"))
        layout.addWidget(self.trainings_table)
    
    def load_teams(self):
        """Загрузка списка команд"""
        teams = self.team_service.get_all_teams()
        
        self.team_combo.clear()
        self.team_combo.addItem("Все команды", None)
        
        for team in teams:
            self.team_combo.addItem(team.name, team.id)
    
    def load_trainings(self):
        """Загрузка списка тренировок с учетом фильтров"""
        team_id = self.team_combo.currentData()
        start_date = self.start_date_edit.date().toPyDate()
        end_date = self.end_date_edit.date().toPyDate()
        
        trainings = self.training_service.get_trainings(team_id, start_date, end_date)
        
        self.trainings_table.setRowCount(0)
        for row, training in enumerate(trainings):
            self.trainings_table.insertRow(row)
            
            self.trainings_table.setItem(row, 0, QTableWidgetItem(str(training.id)))
            self.trainings_table.setItem(row, 1, QTableWidgetItem(format_date(training.date)))
            
            start_time = format_time(training.start_time) if training.start_time else ""
            end_time = format_time(training.end_time) if training.end_time else ""
            self.trainings_table.setItem(row, 2, QTableWidgetItem(f"{start_time} - {end_time}"))
            
            # Расчет продолжительности
            if training.start_time and training.end_time:
                start_minutes = training.start_time.hour * 60 + training.start_time.minute
                end_minutes = training.end_time.hour * 60 + training.end_time.minute
                duration_minutes = end_minutes - start_minutes
                duration = f"{duration_minutes // 60} ч. {duration_minutes % 60} мин."
            else:
                duration = ""
            self.trainings_table.setItem(row, 3, QTableWidgetItem(duration))
            
            team_name = training.team.name if training.team else ""
            self.trainings_table.setItem(row, 4, QTableWidgetItem(team_name))
            
            self.trainings_table.setItem(row, 5, QTableWidgetItem(training.location or ""))
            self.trainings_table.setItem(row, 6, QTableWidgetItem(training.focus_area or ""))
            
            # Расчет посещаемости
            attendance_count = 0
            total_players = 0
            
            if training.attendances:
                total_players = len(training.attendances)
                attendance_count = sum(1 for a in training.attendances if a.is_present)
            
            attendance_text = f"{attendance_count}/{total_players}" if total_players > 0 else "Нет данных"
            self.trainings_table.setItem(row, 7, QTableWidgetItem(attendance_text))
        
        # Выделение цветом тренировок текущего дня
        current_date = QDate.currentDate().toPyDate()
        for row in range(self.trainings_table.rowCount()):
            date_str = self.trainings_table.item(row, 1).text()
            try:
                parts = date_str.split('.')
                if len(parts) == 3:
                    day, month, year = map(int, parts)
                    training_date = datetime.date(year, month, day)
                    if training_date == current_date:
                        for col in range(1, self.trainings_table.columnCount()):
                            item = self.trainings_table.item(row, col)
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
        
        # Загружаем тренировки на выбранную дату
        self.load_trainings()
    
    def add_training(self):
        """Добавление новой тренировки"""
        dialog = TrainingDialog(parent=self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            self.load_trainings()
            show_info_message(self, "Информация", "Тренировка успешно добавлена")
    
    def edit_training(self):
        """Редактирование выбранной тренировки"""
        selected_rows = self.trainings_table.selectedItems()
        if not selected_rows:
            show_error_message(self, "Ошибка", "Необходимо выбрать тренировку для редактирования")
            return
        
        training_id = int(self.trainings_table.item(selected_rows[0].row(), 0).text())
        training = self.training_service.get_training_by_id(training_id)
        
        if not training:
            show_error_message(self, "Ошибка", "Тренировка не найдена")
            return
        
        dialog = TrainingDialog(training, parent=self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            self.load_trainings()
            show_info_message(self, "Информация", "Тренировка успешно обновлена")
    
    def delete_training(self):
        """Удаление выбранной тренировки"""
        selected_rows = self.trainings_table.selectedItems()
        if not selected_rows:
            show_error_message(self, "Ошибка", "Необходимо выбрать тренировку для удаления")
            return
        
        training_id = int(self.trainings_table.item(selected_rows[0].row(), 0).text())
        
        if not show_question_message(self, "Подтверждение", "Вы действительно хотите удалить выбранную тренировку?"):
            return
        
        try:
            self.training_service.delete_training(training_id)
            self.load_trainings()
            show_info_message(self, "Информация", "Тренировка успешно удалена")
        except Exception as e:
            show_error_message(self, "Ошибка", f"Не удалось удалить тренировку: {str(e)}")
    
    def mark_attendance(self):
        """Отметка посещаемости тренировки"""
        selected_rows = self.trainings_table.selectedItems()
        if not selected_rows:
            show_error_message(self, "Ошибка", "Необходимо выбрать тренировку для отметки посещаемости")
            return
        
        training_id = int(self.trainings_table.item(selected_rows[0].row(), 0).text())
        training = self.training_service.get_training_by_id(training_id)
        
        if not training:
            show_error_message(self, "Ошибка", "Тренировка не найдена")
            return
        
        dialog = AttendanceDialog(training, parent=self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            self.load_trainings()
            show_info_message(self, "Информация", "Посещаемость успешно отмечена")
    
    def export_to_excel(self):
        """Экспорт расписания тренировок в Excel"""
        try:
            # Получаем данные из таблицы
            data = []
            headers = ["Дата", "Время", "Продолжительность", "Команда", "Место", "Направление", "Посещаемость"]
            
            for row in range(self.trainings_table.rowCount()):
                row_data = {}
                for col in range(1, self.trainings_table.columnCount()):
                    row_data[headers[col-1]] = self.trainings_table.item(row, col).text()
                data.append(row_data)
            
            # Экспорт в Excel
            filepath = export_to_excel(data, "Расписание_тренировок.xlsx", "Тренировки")
            show_info_message(self, "Экспорт", f"Данные успешно экспортированы в файл:\n{filepath}")
        except Exception as e:
            show_error_message(self, "Ошибка", f"Не удалось экспортировать данные: {str(e)}")

