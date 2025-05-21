# -*- coding: utf-8 -*-

"""
Модуль диалоговых окон приложения
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                           QFormLayout, QLineEdit, QComboBox, QDateEdit, QTimeEdit, 
                           QDialogButtonBox, QTableWidget, QTableWidgetItem, QHeaderView,
                           QCheckBox, QSpinBox, QTextEdit, QGroupBox, QMessageBox,
                           QScrollArea, QWidget, QGridLayout)
from PyQt5.QtCore import Qt, QDate, QTime, pyqtSignal, pyqtSlot, QObject
from PyQt5.QtGui import QFont

import datetime

from database import get_session
from models import Player, Team, Training, Match, TrainingExercise, Tournament, Attendance
from services.player_service import PlayerService
from services.team_service import TeamService
from services.training_service import TrainingService
from services.match_service import MatchService
from utils import (date_to_qdate, time_to_qtime, qdate_to_date, qtime_to_time, 
                 format_date, format_time, show_error_message, show_info_message)


class TrainingDialog(QDialog):
    """Диалог добавления/редактирования тренировки"""
    
    def __init__(self, training=None, parent=None):
        super().__init__(parent)
        
        self.training = training
        self.team_service = TeamService()
        self.training_service = TrainingService()
        
        self.init_ui()
        
        if training:
            self.setWindowTitle("Редактирование тренировки")
            self.load_training_data()
        else:
            self.setWindowTitle("Добавление тренировки")
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QFormLayout(self)
        
        # Дата тренировки
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        layout.addRow("Дата:", self.date_edit)
        
        # Время начала
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setTime(QTime(18, 0))
        layout.addRow("Время начала:", self.start_time_edit)
        
        # Время окончания
        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setTime(QTime(19, 30))
        layout.addRow("Время окончания:", self.end_time_edit)
        
        # Команда
        self.team_combo = QComboBox()
        self.load_teams()
        layout.addRow("Команда:", self.team_combo)
        
        # Место проведения
        self.location_edit = QLineEdit()
        layout.addRow("Место проведения:", self.location_edit)
        
        # Направление тренировки
        self.focus_area_combo = QComboBox()
        self.focus_area_combo.addItems([
            "Физическая подготовка", 
            "Тактика", 
            "Техника катания", 
            "Техника владения клюшкой",
            "Броски",
            "Комплексная",
            "Игровая",
            "Восстановительная"
        ])
        layout.addRow("Направление:", self.focus_area_combo)
        
        # Описание
        self.description_edit = QTextEdit()
        self.description_edit.setMinimumHeight(100)
        layout.addRow("Описание:", self.description_edit)
        
        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setMinimumWidth(400)
    
    def load_teams(self):
        """Загрузка списка команд"""
        teams = self.team_service.get_all_teams()
        
        self.team_combo.clear()
        for team in teams:
            self.team_combo.addItem(team.name, team.id)
    
    def load_training_data(self):
        """Загрузка данных тренировки"""
        if not self.training:
            return
        
        # Установка даты
        if self.training.date:
            self.date_edit.setDate(date_to_qdate(self.training.date))
        
        # Установка времени
        if self.training.start_time:
            self.start_time_edit.setTime(time_to_qtime(self.training.start_time))
        
        if self.training.end_time:
            self.end_time_edit.setTime(time_to_qtime(self.training.end_time))
        
        # Установка команды
        if self.training.team_id:
            index = self.team_combo.findData(self.training.team_id)
            if index >= 0:
                self.team_combo.setCurrentIndex(index)
        
        # Установка места
        if self.training.location:
            self.location_edit.setText(self.training.location)
        
        # Установка направления
        if self.training.focus_area:
            index = self.focus_area_combo.findText(self.training.focus_area)
            if index >= 0:
                self.focus_area_combo.setCurrentIndex(index)
        
        # Установка описания
        if self.training.description:
            self.description_edit.setText(self.training.description)
    
    def get_training_data(self):
        """Получение данных тренировки из полей формы"""
        data = {
            'date': self.date_edit.date().toPyDate(),
            'start_time': self.start_time_edit.time().toPyTime(),
            'end_time': self.end_time_edit.time().toPyTime(),
            'team_id': self.team_combo.currentData(),
            'location': self.location_edit.text().strip(),
            'focus_area': self.focus_area_combo.currentText(),
            'description': self.description_edit.toPlainText().strip()
        }
        return data
    
    def accept(self):
        """Обработка нажатия кнопки OK"""
        training_data = self.get_training_data()
        
        # Проверка обязательных полей
        if not training_data['date'] or not training_data['team_id']:
            show_error_message(self, "Ошибка", "Дата и команда обязательны для заполнения")
            return
        
        try:
            if self.training:
                # Обновление тренировки
                self.training_service.update_training(self.training.id, training_data)
            else:
                # Создание новой тренировки
                self.training_service.create_training(training_data)
            
            super().accept()
        except Exception as e:
            show_error_message(self, "Ошибка", f"Не удалось сохранить данные тренировки: {str(e)}")


class MatchDialog(QDialog):
    """Диалог добавления/редактирования матча"""
    
    def __init__(self, match=None, parent=None):
        super().__init__(parent)
        
        self.match = match
        self.team_service = TeamService()
        self.match_service = MatchService()
        
        self.init_ui()
        
        if match:
            self.setWindowTitle("Редактирование матча")
            self.load_match_data()
        else:
            self.setWindowTitle("Добавление матча")
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QFormLayout(self)
        
        # Дата матча
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        layout.addRow("Дата:", self.date_edit)
        
        # Время матча
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime(18, 0))
        layout.addRow("Время:", self.time_edit)
        
        # Домашняя команда
        self.home_team_combo = QComboBox()
        self.load_teams(self.home_team_combo)
        layout.addRow("Домашняя команда:", self.home_team_combo)
        
        # Команда гостей
        self.away_team_combo = QComboBox()
        self.load_teams(self.away_team_combo)
        layout.addRow("Команда гостей:", self.away_team_combo)
        
        # Место проведения
        self.location_edit = QLineEdit()
        layout.addRow("Место проведения:", self.location_edit)
        
        # Статус матча
        self.status_combo = QComboBox()
        self.status_combo.addItems(["запланирован", "завершен", "отменен"])
        layout.addRow("Статус:", self.status_combo)
        
        # Примечания
        self.notes_edit = QTextEdit()
        self.notes_edit.setMinimumHeight(100)
        layout.addRow("Примечания:", self.notes_edit)
        
        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setMinimumWidth(400)
    
    def load_teams(self, combo):
        """Загрузка списка команд"""
        teams = self.team_service.get_all_teams()
        
        combo.clear()
        for team in teams:
            combo.addItem(team.name, team.id)
    
    def load_match_data(self):
        """Загрузка данных матча"""
        if not self.match:
            return
        
        # Установка даты
        if self.match.date:
            self.date_edit.setDate(date_to_qdate(self.match.date))
        
        # Установка времени
        if self.match.time:
            self.time_edit.setTime(time_to_qtime(self.match.time))
        
        # Установка домашней команды
        if self.match.home_team_id:
            index = self.home_team_combo.findData(self.match.home_team_id)
            if index >= 0:
                self.home_team_combo.setCurrentIndex(index)
        
        # Установка команды гостей
        if self.match.away_team_id:
            index = self.away_team_combo.findData(self.match.away_team_id)
            if index >= 0:
                self.away_team_combo.setCurrentIndex(index)
        
        # Установка места
        if self.match.location:
            self.location_edit.setText(self.match.location)
        
        # Установка статуса
        if self.match.status:
            index = self.status_combo.findText(self.match.status)
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
        
        # Установка примечаний
        if self.match.notes:
            self.notes_edit.setText(self.match.notes)
    
    def get_match_data(self):
        """Получение данных матча из полей формы"""
        data = {
            'date': self.date_edit.date().toPyDate(),
            'time': self.time_edit.time().toPyTime(),
            'home_team_id': self.home_team_combo.currentData(),
            'away_team_id': self.away_team_combo.currentData(),
            'location': self.location_edit.text().strip(),
            'status': self.status_combo.currentText(),
            'notes': self.notes_edit.toPlainText().strip()
        }
        return data
    
    def accept(self):
        """Обработка нажатия кнопки OK"""
        match_data = self.get_match_data()
        
        # Проверка обязательных полей
        if not match_data['date'] or not match_data['home_team_id'] or not match_data['away_team_id']:
            show_error_message(self, "Ошибка", "Дата, домашняя команда и команда гостей обязательны для заполнения")
            return
        
        # Проверка, что команды разные
        if match_data['home_team_id'] == match_data['away_team_id']:
            show_error_message(self, "Ошибка", "Домашняя команда и команда гостей должны быть разными")
            return
        
        try:
            if self.match:
                # Обновление матча
                self.match_service.update_match(self.match.id, match_data)
            else:
                # Создание нового матча
                self.match_service.create_match(match_data)
            
            super().accept()
        except Exception as e:
            show_error_message(self, "Ошибка", f"Не удалось сохранить данные матча: {str(e)}")


class MatchResultsDialog(QDialog):
    """Диалог для внесения результатов матча"""
    
    def __init__(self, match, parent=None):
        super().__init__(parent)
        
        self.match = match
        self.match_service = MatchService()
        
        self.init_ui()
        self.load_match_data()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("Внесение результатов матча")
        layout = QFormLayout(self)
        
        # Информация о матче
        match_info = ""
        if self.match:
            date_str = format_date(self.match.date) if self.match.date else ""
            home_team = self.match.home_team.name if self.match.home_team else ""
            away_team = self.match.away_team.name if self.match.away_team else ""
            match_info = f"{date_str}: {home_team} - {away_team}"
        
        info_label = QLabel(match_info)
        info_label.setStyleSheet("font-weight: bold;")
        layout.addRow("Матч:", info_label)
        
        # Счет матча
        score_layout = QHBoxLayout()
        
        # Голы домашней команды
        self.home_score_spin = QSpinBox()
        self.home_score_spin.setMinimum(0)
        self.home_score_spin.setMaximum(99)
        score_layout.addWidget(QLabel("Голы хозяев:"))
        score_layout.addWidget(self.home_score_spin)
        
        score_layout.addWidget(QLabel(" : "))
        
        # Голы команды гостей
        self.away_score_spin = QSpinBox()
        self.away_score_spin.setMinimum(0)
        self.away_score_spin.setMaximum(99)
        score_layout.addWidget(self.away_score_spin)
        score_layout.addWidget(QLabel("Голы гостей"))
        
        score_layout.addStretch()
        
        layout.addRow("Счет:", score_layout)
        
        # Статус матча
        self.status_combo = QComboBox()
        self.status_combo.addItems(["запланирован", "завершен", "отменен"])
        layout.addRow("Статус:", self.status_combo)
        
        # Примечания
        self.notes_edit = QTextEdit()
        self.notes_edit.setMinimumHeight(100)
        layout.addRow("Примечания:", self.notes_edit)
        
        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setMinimumWidth(400)
    
    def load_match_data(self):
        """Загрузка данных матча"""
        if not self.match:
            return
        
        # Установка счета
        if self.match.home_score is not None:
            self.home_score_spin.setValue(self.match.home_score)
        
        if self.match.away_score is not None:
            self.away_score_spin.setValue(self.match.away_score)
        
        # Установка статуса
        if self.match.status:
            index = self.status_combo.findText(self.match.status)
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
        
        # Установка примечаний
        if self.match.notes:
            self.notes_edit.setText(self.match.notes)
    
    def get_match_data(self):
        """Получение данных матча из полей формы"""
        data = {
            'home_score': self.home_score_spin.value(),
            'away_score': self.away_score_spin.value(),
            'status': self.status_combo.currentText(),
            'notes': self.notes_edit.toPlainText().strip()
        }
        return data
    
    def accept(self):
        """Обработка нажатия кнопки OK"""
        match_data = self.get_match_data()
        
        try:
            # Обновление результатов матча
            self.match_service.update_match_results(self.match.id, match_data)
            super().accept()
        except Exception as e:
            show_error_message(self, "Ошибка", f"Не удалось сохранить результаты матча: {str(e)}")


class AttendanceDialog(QDialog):
    """Диалог для отметки посещаемости тренировки"""
    
    def __init__(self, training, parent=None):
        super().__init__(parent)
        
        self.training = training
        self.training_service = TrainingService()
        self.player_service = PlayerService()
        
        self.init_ui()
        self.load_attendance_data()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("Отметка посещаемости")
        layout = QVBoxLayout(self)
        
        # Информация о тренировке
        info_layout = QFormLayout()
        
        training_info = ""
        if self.training:
            date_str = format_date(self.training.date) if self.training.date else ""
            team_name = self.training.team.name if self.training.team else ""
            time_str = ""
            if self.training.start_time and self.training.end_time:
                time_str = f"{format_time(self.training.start_time)} - {format_time(self.training.end_time)}"
            
            training_info = f"{date_str} {time_str}"
        
        self.info_label = QLabel(training_info)
        self.info_label.setStyleSheet("font-weight: bold;")
        info_layout.addRow("Тренировка:", self.info_label)
        
        self.team_label = QLabel(self.training.team.name if self.training.team else "")
        info_layout.addRow("Команда:", self.team_label)
        
        layout.addLayout(info_layout)
        
        # Таблица игроков для отметки посещаемости
        self.attendance_table = QTableWidget()
        self.attendance_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.attendance_table.setSelectionMode(QTableWidget.SingleSelection)
        self.attendance_table.setColumnCount(4)
        self.attendance_table.setHorizontalHeaderLabels([
            "ID", "Игрок", "Присутствие", "Причина отсутствия"
        ])
        self.attendance_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.attendance_table.setColumnHidden(0, True)  # Скрываем ID
        
        layout.addWidget(self.attendance_table)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        all_present_button = QPushButton("Все присутствуют")
        all_present_button.clicked.connect(self.mark_all_present)
        buttons_layout.addWidget(all_present_button)
        
        all_absent_button = QPushButton("Все отсутствуют")
        all_absent_button.clicked.connect(self.mark_all_absent)
        buttons_layout.addWidget(all_absent_button)
        
        buttons_layout.addStretch()
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        buttons_layout.addWidget(button_box)
        
        layout.addLayout(buttons_layout)
        
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
    
    def load_attendance_data(self):
        """Загрузка данных о посещаемости"""
        if not self.training or not self.training.team_id:
            return
        
        # Получаем список игроков команды
        players = self.player_service.get_players(self.training.team_id)
        
        # Получаем существующие записи о посещаемости
        attendances = self.training_service.get_training_attendance(self.training.id)
        
        attendance_dict = {}
        for attendance in attendances:
            attendance_dict[attendance.player_id] = attendance
        
        # Заполняем таблицу
        self.attendance_table.setRowCount(len(players))
        
        for row, player in enumerate(players):
            # ID игрока
            self.attendance_table.setItem(row, 0, QTableWidgetItem(str(player.id)))
            
            # Имя игрока
            self.attendance_table.setItem(row, 1, QTableWidgetItem(player.full_name))
            
            # Чекбокс присутствия
            checkbox = QCheckBox()
            self.attendance_table.setCellWidget(row, 2, checkbox)
            
            # Причина отсутствия
            reason_edit = QLineEdit()
            self.attendance_table.setCellWidget(row, 3, reason_edit)
            
            # Устанавливаем значения из существующих записей
            if player.id in attendance_dict:
                attendance = attendance_dict[player.id]
                checkbox.setChecked(attendance.is_present)
                if attendance.reason:
                    reason_edit.setText(attendance.reason)
                
                # Если игрок присутствует, блокируем поле причины
                reason_edit.setEnabled(not attendance.is_present)
            
            # Связываем чекбокс с полем причины
            checkbox.stateChanged.connect(lambda state, row=row: self.toggle_reason_field(row, state))
    
    def toggle_reason_field(self, row, state):
        """Включение/отключение поля причины в зависимости от состояния чекбокса"""
        reason_edit = self.attendance_table.cellWidget(row, 3)
        if reason_edit:
            # Если отмечено присутствие, отключаем поле причины и очищаем его
            is_present = state == Qt.Checked
            reason_edit.setEnabled(not is_present)
            if is_present:
                reason_edit.clear()
    
    def mark_all_present(self):
        """Отметить всех игроков как присутствующих"""
        for row in range(self.attendance_table.rowCount()):
            checkbox = self.attendance_table.cellWidget(row, 2)
            if checkbox:
                checkbox.setChecked(True)
    
    def mark_all_absent(self):
        """Отметить всех игроков как отсутствующих"""
        for row in range(self.attendance_table.rowCount()):
            checkbox = self.attendance_table.cellWidget(row, 2)
            if checkbox:
                checkbox.setChecked(False)
    
    def get_attendance_data(self):
        """Получение данных о посещаемости из таблицы"""
        data = []
        
        for row in range(self.attendance_table.rowCount()):
            player_id = int(self.attendance_table.item(row, 0).text())
            checkbox = self.attendance_table.cellWidget(row, 2)
            reason_edit = self.attendance_table.cellWidget(row, 3)
            
            is_present = checkbox.isChecked() if checkbox else False
            reason = reason_edit.text().strip() if reason_edit and not is_present else None
            
            data.append({
                'player_id': player_id,
                'is_present': is_present,
                'reason': reason
            })
        
        return data
    
    def accept(self):
        """Обработка нажатия кнопки OK"""
        attendance_data = self.get_attendance_data()
        
        try:
            # Сохранение данных о посещаемости
            self.training_service.update_attendance(self.training.id, attendance_data)
            super().accept()
        except Exception as e:
            show_error_message(self, "Ошибка", f"Не удалось сохранить данные о посещаемости: {str(e)}")


class ExerciseDialog(QDialog):
    """Диалог добавления/редактирования упражнения"""
    
    def __init__(self, training_id, order, exercise=None, parent=None):
        super().__init__(parent)
        
        self.training_id = training_id
        self.order = order
        self.exercise = exercise
        self.training_service = TrainingService()
        
        self.init_ui()
        
        if exercise:
            self.setWindowTitle("Редактирование упражнения")
            self.load_exercise_data()
        else:
            self.setWindowTitle("Добавление упражнения")
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QFormLayout(self)
        
        # Название упражнения
        self.name_edit = QLineEdit()
        layout.addRow("Название:", self.name_edit)
        
        # Продолжительность
        self.duration_spin = QSpinBox()
        self.duration_spin.setMinimum(1)
        self.duration_spin.setMaximum(120)
        self.duration_spin.setSuffix(" мин.")
        layout.addRow("Продолжительность:", self.duration_spin)
        
        # Порядковый номер
        self.order_spin = QSpinBox()
        self.order_spin.setMinimum(1)
        self.order_spin.setMaximum(100)
        self.order_spin.setValue(self.order)
        layout.addRow("Порядковый номер:", self.order_spin)
        
        # Описание
        self.description_edit = QTextEdit()
        self.description_edit.setMinimumHeight(150)
        layout.addRow("Описание:", self.description_edit)
        
        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setMinimumWidth(400)
    
    def load_exercise_data(self):
        """Загрузка данных упражнения"""
        if not self.exercise:
            return
        
        self.name_edit.setText(self.exercise.name)
        
        if self.exercise.duration:
            self.duration_spin.setValue(self.exercise.duration)
        
        if self.exercise.order:
            self.order_spin.setValue(self.exercise.order)
        
        if self.exercise.description:
            self.description_edit.setText(self.exercise.description)
    
    def get_exercise_data(self):
        """Получение данных упражнения из полей формы"""
        data = {
            'training_id': self.training_id,
            'name': self.name_edit.text().strip(),
            'duration': self.duration_spin.value(),
            'order': self.order_spin.value(),
            'description': self.description_edit.toPlainText().strip()
        }
        return data
    
    def accept(self):
        """Обработка нажатия кнопки OK"""
        exercise_data = self.get_exercise_data()
        
        # Проверка обязательных полей
        if not exercise_data['name']:
            show_error_message(self, "Ошибка", "Название упражнения обязательно для заполнения")
            return
        
        try:
            if self.exercise:
                # Обновление упражнения
                self.training_service.update_exercise(self.exercise.id, exercise_data)
            else:
                # Создание нового упражнения
                self.training_service.create_exercise(exercise_data)
            
            super().accept()
        except Exception as e:
            show_error_message(self, "Ошибка", f"Не удалось сохранить данные упражнения: {str(e)}")


class TournamentDialog(QDialog):
    """Диалог добавления/редактирования турнира"""
    
    def __init__(self, tournament=None, parent=None):
        super().__init__(parent)
        
        self.tournament = tournament
        self.team_service = TeamService()
        
        self.init_ui()
        
        if tournament:
            self.setWindowTitle("Редактирование турнира")
            self.load_tournament_data()
        else:
            self.setWindowTitle("Добавление турнира")
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QFormLayout(self)
        
        # Название турнира
        self.name_edit = QLineEdit()
        layout.addRow("Название:", self.name_edit)
        
        # Даты проведения
        dates_layout = QHBoxLayout()
        
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())
        dates_layout.addWidget(self.start_date_edit)
        
        dates_layout.addWidget(QLabel(" - "))
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate().addDays(7))
        dates_layout.addWidget(self.end_date_edit)
        
        layout.addRow("Даты проведения:", dates_layout)
        
        # Место проведения
        self.location_edit = QLineEdit()
        layout.addRow("Место проведения:", self.location_edit)
        
        # Описание
        self.description_edit = QTextEdit()
        self.description_edit.setMinimumHeight(100)
        layout.addRow("Описание:", self.description_edit)
        
        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setMinimumWidth(400)
    
    def load_tournament_data(self):
        """Загрузка данных турнира"""
        if not self.tournament:
            return
        
        self.name_edit.setText(self.tournament.name)
        
        if self.tournament.start_date:
            self.start_date_edit.setDate(date_to_qdate(self.tournament.start_date))
        
        if self.tournament.end_date:
            self.end_date_edit.setDate(date_to_qdate(self.tournament.end_date))
        
        if self.tournament.location:
            self.location_edit.setText(self.tournament.location)
        
        if self.tournament.description:
            self.description_edit.setText(self.tournament.description)
    
    def get_tournament_data(self):
        """Получение данных турнира из полей формы"""
        data = {
            'name': self.name_edit.text().strip(),
            'start_date': self.start_date_edit.date().toPyDate(),
            'end_date': self.end_date_edit.date().toPyDate(),
            'location': self.location_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip()
        }
        return data
    
    def accept(self):
        """Обработка нажатия кнопки OK"""
        tournament_data = self.get_tournament_data()
        
        # Проверка обязательных полей
        if not tournament_data['name']:
            show_error_message(self, "Ошибка", "Название турнира обязательно для заполнения")
            return
        
        # Проверка дат
        if tournament_data['start_date'] > tournament_data['end_date']:
            show_error_message(self, "Ошибка", "Дата начала не может быть позже даты окончания")
            return
        
        try:
            if self.tournament:
                # Обновление турнира
                self.team_service.update_tournament(self.tournament.id, tournament_data)
            else:
                # Создание нового турнира
                self.team_service.create_tournament(tournament_data)
            
            super().accept()
        except Exception as e:
            show_error_message(self, "Ошибка", f"Не удалось сохранить данные турнира: {str(e)}")


class AddTeamToTournamentDialog(QDialog):
    """Диалог добавления команды в турнир"""
    
    def __init__(self, tournament_id, parent=None):
        super().__init__(parent)
        
        self.tournament_id = tournament_id
        self.team_service = TeamService()
        
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("Добавление команды в турнир")
        layout = QFormLayout(self)
        
        # Выбор команды
        self.team_combo = QComboBox()
        self.load_teams()
        layout.addRow("Команда:", self.team_combo)
        
        # Место в турнире
        self.rank_spin = QSpinBox()
        self.rank_spin.setMinimum(0)
        self.rank_spin.setMaximum(100)
        self.rank_spin.setSpecialValueText("Не определено")
        layout.addRow("Место в турнире:", self.rank_spin)
        
        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setMinimumWidth(300)
    
    def load_teams(self):
        """Загрузка списка команд, не участвующих в турнире"""
        teams = self.team_service.get_available_teams_for_tournament(self.tournament_id)
        
        self.team_combo.clear()
        
        if not teams:
            self.team_combo.addItem("Нет доступных команд", None)
            return
        
        for team in teams:
            self.team_combo.addItem(team.name, team.id)
    
    def get_data(self):
        """Получение данных из полей формы"""
        team_id = self.team_combo.currentData()
        rank = self.rank_spin.value() if self.rank_spin.value() > 0 else None
        
        return {
            'tournament_id': self.tournament_id,
            'team_id': team_id,
            'rank': rank
        }
    
    def accept(self):
        """Обработка нажатия кнопки OK"""
        data = self.get_data()
        
        # Проверка выбора команды
        if not data['team_id']:
            show_error_message(self, "Ошибка", "Необходимо выбрать команду")
            return
        
        try:
            # Добавление команды в турнир
            self.team_service.add_team_to_tournament(data)
            super().accept()
        except Exception as e:
            show_error_message(self, "Ошибка", f"Не удалось добавить команду в турнир: {str(e)}")


class TeamDialog(QDialog):
    """Диалог для добавления/редактирования команды"""
    
    def __init__(self, team=None, create_mode="full", parent=None):
        super().__init__(parent)
        
        self.team = team
        self.create_mode = create_mode  # "quick" - только название, "basic" - базовые поля, "full" - все поля
        self.team_service = TeamService()
        
        self.init_ui()
        
        if team:
            self.setWindowTitle("Редактирование команды")
            self.load_team_data()
        else:
            if self.create_mode == "quick":
                self.setWindowTitle("Быстрое создание команды")
            elif self.create_mode == "basic":
                self.setWindowTitle("Создание команды (базовые параметры)")
            else:
                self.setWindowTitle("Полное создание команды")
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QFormLayout(self)
        
        # Название команды (есть во всех режимах)
        self.name_edit = QLineEdit()
        layout.addRow("Название команды:", self.name_edit)
        
        # Базовые поля (для режимов basic и full)
        if self.create_mode in ["basic", "full"]:
            # Год основания
            self.foundation_year_spin = QSpinBox()
            self.foundation_year_spin.setMinimum(1900)
            self.foundation_year_spin.setMaximum(2100)
            self.foundation_year_spin.setValue(2023)
            layout.addRow("Год основания:", self.foundation_year_spin)
            
            # Описание
            self.description_edit = QTextEdit()
            layout.addRow("Описание команды:", self.description_edit)
        
        # Полные поля (только для режима full)
        if self.create_mode == "full":
            # Домашняя арена
            self.home_arena_edit = QLineEdit()
            layout.addRow("Домашняя арена:", self.home_arena_edit)
            
            # Признак команды-соперника
            self.is_opponent_check = QCheckBox("Команда-соперник")
            layout.addRow("", self.is_opponent_check)
        
        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setMinimumWidth(350)
    
    def load_team_data(self):
        """Загрузка данных команды"""
        if not self.team:
            return
        
        self.name_edit.setText(self.team.name)
        
        if self.create_mode in ["basic", "full"]:
            if self.team.foundation_year:
                self.foundation_year_spin.setValue(self.team.foundation_year)
            
            if self.team.description:
                self.description_edit.setText(self.team.description)
        
        if self.create_mode == "full":
            if self.team.home_arena:
                self.home_arena_edit.setText(self.team.home_arena)
            
            self.is_opponent_check.setChecked(self.team.is_opponent)
    
    def get_team_data(self):
        """Получение данных команды из полей формы"""
        team_data = {
            'name': self.name_edit.text().strip(),
            'is_opponent': False  # По умолчанию не соперник
        }
        
        if self.create_mode in ["basic", "full"]:
            team_data.update({
                'foundation_year': self.foundation_year_spin.value(),
                'description': self.description_edit.toPlainText().strip() or None
            })
        
        if self.create_mode == "full":
            team_data.update({
                'home_arena': self.home_arena_edit.text().strip() or None,
                'is_opponent': self.is_opponent_check.isChecked()
            })
        
        return team_data
    
    def accept(self):
        """Обработка нажатия кнопки OK"""
        team_data = self.get_team_data()
        
        # Проверка обязательных полей
        if not team_data['name']:
            show_error_message(self, "Ошибка", "Название команды обязательно для заполнения")
            return
        
        try:
            if self.team:
                # Обновление команды
                self.team_service.update_team(self.team.id, team_data)
            else:
                # Создание новой команды
                self.team_service.create_team(team_data)
            
            super().accept()
        except Exception as e:
            show_error_message(self, "Ошибка", f"Не удалось сохранить данные команды: {str(e)}")

