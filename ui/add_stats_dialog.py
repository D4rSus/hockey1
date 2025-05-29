
# -*- coding: utf-8 -*-

"""
Диалог для добавления статистики игрока
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                           QPushButton, QLabel, QSpinBox, QComboBox, QTimeEdit,
                           QMessageBox, QDateEdit, QTextEdit)
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QFont

from services.match_service import MatchService
from services.stats_service import StatsService
from utils import show_error_message, show_info_message

class AddStatsDialog(QDialog):
    """Диалог для добавления статистики игрока"""
    
    def __init__(self, player, parent=None):
        super().__init__(parent)
        
        self.player = player
        self.match_service = MatchService()
        self.stats_service = StatsService()
        
        self.setWindowTitle(f"Добавить статистику - {player.last_name} {player.first_name}")
        self.setModal(True)
        self.resize(400, 500)
        
        self.init_ui()
        self.load_matches()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout(self)
        
        # Заголовок
        title_label = QLabel(f"Добавление статистики для игрока:")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        player_label = QLabel(f"{self.player.last_name} {self.player.first_name}")
        player_font = QFont()
        player_font.setPointSize(10)
        player_label.setFont(player_font)
        layout.addWidget(player_label)
        
        # Форма
        form_layout = QFormLayout()
        
        # Выбор матча
        self.match_combo = QComboBox()
        self.match_combo.addItem("Новый матч", None)
        form_layout.addRow("Матч:", self.match_combo)
        
        # Дата матча (для нового матча)
        self.match_date = QDateEdit()
        self.match_date.setDate(QDate.currentDate())
        self.match_date.setCalendarPopup(True)
        form_layout.addRow("Дата матча:", self.match_date)
        
        # Соперник (для нового матча)
        self.opponent_combo = QComboBox()
        self.opponent_combo.setEditable(True)
        form_layout.addRow("Соперник:", self.opponent_combo)
        
        # Статистика игрока
        self.goals_spin = QSpinBox()
        self.goals_spin.setRange(0, 20)
        form_layout.addRow("Голы:", self.goals_spin)
        
        self.assists_spin = QSpinBox()
        self.assists_spin.setRange(0, 20)
        form_layout.addRow("Передачи:", self.assists_spin)
        
        self.penalty_spin = QSpinBox()
        self.penalty_spin.setRange(0, 60)
        self.penalty_spin.setSuffix(" мин")
        form_layout.addRow("Штрафное время:", self.penalty_spin)
        
        self.plus_minus_spin = QSpinBox()
        self.plus_minus_spin.setRange(-10, 10)
        form_layout.addRow("+/-:", self.plus_minus_spin)
        
        self.shots_spin = QSpinBox()
        self.shots_spin.setRange(0, 50)
        form_layout.addRow("Броски:", self.shots_spin)
        
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime(0, 0))
        self.time_edit.setDisplayFormat("mm:ss")
        form_layout.addRow("Время на льду:", self.time_edit)
        
        self.faceoffs_won_spin = QSpinBox()
        self.faceoffs_won_spin.setRange(0, 100)
        form_layout.addRow("Выиграно вбрасываний:", self.faceoffs_won_spin)
        
        self.faceoffs_total_spin = QSpinBox()
        self.faceoffs_total_spin.setRange(0, 100)
        form_layout.addRow("Всего вбрасываний:", self.faceoffs_total_spin)
        
        # Заметки
        self.notes_text = QTextEdit()
        self.notes_text.setMaximumHeight(60)
        self.notes_text.setPlaceholderText("Дополнительные заметки о матче...")
        form_layout.addRow("Заметки:", self.notes_text)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_stats)
        buttons_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)
        
        # Подключение сигналов
        self.match_combo.currentIndexChanged.connect(self.on_match_changed)
        self.faceoffs_won_spin.valueChanged.connect(self.validate_faceoffs)
        self.faceoffs_total_spin.valueChanged.connect(self.validate_faceoffs)
    
    def load_matches(self):
        """Загрузка списка матчей"""
        try:
            # Получаем команды для выбора соперника
            from services.team_service import TeamService
            team_service = TeamService()
            teams = team_service.get_all_teams()
            
            for team in teams:
                if team.id != self.player.team_id:  # Исключаем команду игрока
                    self.opponent_combo.addItem(team.name, team.id)
            
            # Получаем недавние матчи команды игрока
            matches = self.match_service.get_team_matches(self.player.team_id, limit=10)
            
            for match in matches:
                match_text = f"{match['date']} - {match['opponent']}"
                self.match_combo.addItem(match_text, match['match_id'])
                
        except Exception as e:
            print(f"Ошибка при загрузке матчей: {str(e)}")
    
    def on_match_changed(self):
        """Обработка изменения выбранного матча"""
        match_id = self.match_combo.currentData()
        
        # Показываем/скрываем поля для нового матча
        is_new_match = match_id is None
        self.match_date.setVisible(is_new_match)
        self.opponent_combo.setVisible(is_new_match)
        
        # Находим строки формы для скрытия/показа
        form_layout = self.layout().itemAt(2).layout()
        for i in range(form_layout.rowCount()):
            item = form_layout.itemAt(i, QFormLayout.LabelRole)
            if item and item.widget():
                label_text = item.widget().text()
                if label_text in ["Дата матча:", "Соперник:"]:
                    item.widget().setVisible(is_new_match)
                    field_item = form_layout.itemAt(i, QFormLayout.FieldRole)
                    if field_item and field_item.widget():
                        field_item.widget().setVisible(is_new_match)
    
    def validate_faceoffs(self):
        """Валидация данных по вбрасываниям"""
        won = self.faceoffs_won_spin.value()
        total = self.faceoffs_total_spin.value()
        
        if won > total:
            self.faceoffs_total_spin.setValue(won)
    
    def save_stats(self):
        """Сохранение статистики"""
        try:
            match_id = self.match_combo.currentData()
            
            # Если выбран новый матч, создаем его
            if match_id is None:
                opponent_id = self.opponent_combo.currentData()
                if not opponent_id:
                    show_error_message(self, "Ошибка", "Выберите команду соперника")
                    return
                
                # Создаем новый матч
                match_data = {
                    'date': self.match_date.date().toPyDate(),
                    'home_team_id': self.player.team_id,
                    'away_team_id': opponent_id,
                    'status': 'завершен'
                }
                
                match_id = self.match_service.create_match(match_data)
                if not match_id:
                    show_error_message(self, "Ошибка", "Не удалось создать матч")
                    return
            
            # Подготавливаем данные статистики
            time_on_ice_minutes = self.time_edit.time().minute()
            time_on_ice_seconds = self.time_edit.time().second()
            time_on_ice_total = time_on_ice_minutes * 60 + time_on_ice_seconds
            
            stats_data = {
                'goals': self.goals_spin.value(),
                'assists': self.assists_spin.value(),
                'penalty_minutes': self.penalty_spin.value(),
                'plus_minus': self.plus_minus_spin.value(),
                'shots': self.shots_spin.value(),
                'time_on_ice': time_on_ice_total,
                'faceoffs_won': self.faceoffs_won_spin.value(),
                'faceoffs_total': self.faceoffs_total_spin.value()
            }
            
            # Сохраняем статистику
            result = self.stats_service.update_player_match_stats(
                self.player.id, 
                match_id, 
                stats_data
            )
            
            if result:
                show_info_message(self, "Успех", "Статистика успешно добавлена")
                self.accept()
            else:
                show_error_message(self, "Ошибка", "Не удалось сохранить статистику")
                
        except Exception as e:
            show_error_message(self, "Ошибка", f"Ошибка при сохранении: {str(e)}")
