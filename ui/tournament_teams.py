# -*- coding: utf-8 -*-

"""
Виджет для отображения и управления командами, участвующими в турнире
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                          QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                          QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QGroupBox,
                          QDateEdit, QMessageBox, QSpinBox)
from PyQt5.QtCore import QDate, Qt, pyqtSignal

from models import Tournament, TournamentTeam, Team
from services.team_service import TeamService
from ui.dialogs import TournamentDialog, AddTeamToTournamentDialog
from utils import (format_date, show_error_message, show_info_message, 
                 show_question_message, export_to_excel, date_to_qdate)

class TournamentTeamsWidget(QWidget):
    """Виджет для отображения и управления командами, участвующими в турнире"""
    
    def __init__(self):
        super().__init__()
        
        self.team_service = TeamService()
        
        self.init_ui()
        self.load_tournaments()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout(self)
        
        # Панель выбора турнира и элементов управления
        control_layout = QHBoxLayout()
        
        # Выбор турнира
        control_layout.addWidget(QLabel("Турнир:"))
        self.tournament_combo = QComboBox()
        self.tournament_combo.setMinimumWidth(300)
        self.tournament_combo.currentIndexChanged.connect(self.load_teams)
        control_layout.addWidget(self.tournament_combo)
        
        control_layout.addStretch()
        
        # Кнопки управления турнирами
        manage_tournaments_button = QPushButton("Управление турнирами")
        manage_tournaments_button.clicked.connect(self.manage_tournaments)
        control_layout.addWidget(manage_tournaments_button)
        
        add_tournament_button = QPushButton("Добавить турнир")
        add_tournament_button.clicked.connect(self.add_tournament)
        control_layout.addWidget(add_tournament_button)
        
        # Кнопка экспорта
        export_button = QPushButton("Экспорт")
        export_button.clicked.connect(self.export_to_excel)
        control_layout.addWidget(export_button)
        
        layout.addLayout(control_layout)
        
        # Блок информации о турнире
        tournament_info_group = QGroupBox("Информация о турнире")
        info_layout = QFormLayout(tournament_info_group)
        
        self.tournament_name_label = QLabel()
        info_layout.addRow("Название:", self.tournament_name_label)
        
        self.tournament_dates_label = QLabel()
        info_layout.addRow("Даты проведения:", self.tournament_dates_label)
        
        self.tournament_location_label = QLabel()
        info_layout.addRow("Место проведения:", self.tournament_location_label)
        
        self.tournament_description_label = QLabel()
        self.tournament_description_label.setWordWrap(True)
        info_layout.addRow("Описание:", self.tournament_description_label)
        
        layout.addWidget(tournament_info_group)
        
        # Таблица команд-участников
        layout.addWidget(QLabel("Команды-участники:"))
        
        self.teams_table = QTableWidget()
        self.teams_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.teams_table.setSelectionMode(QTableWidget.SingleSelection)
        self.teams_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.teams_table.setColumnCount(4)
        self.teams_table.setHorizontalHeaderLabels([
            "ID", "Команда", "Место в турнире", "Примечания"
        ])
        self.teams_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.teams_table.setColumnHidden(0, True)  # Скрываем ID
        
        layout.addWidget(self.teams_table)
        
        # Кнопки управления командами
        teams_buttons_layout = QHBoxLayout()
        
        add_team_button = QPushButton("Добавить команду")
        add_team_button.clicked.connect(self.add_team)
        teams_buttons_layout.addWidget(add_team_button)
        
        remove_team_button = QPushButton("Удалить команду")
        remove_team_button.clicked.connect(self.remove_team)
        teams_buttons_layout.addWidget(remove_team_button)
        
        update_rank_button = QPushButton("Обновить места")
        update_rank_button.clicked.connect(self.update_rank)
        teams_buttons_layout.addWidget(update_rank_button)
        
        layout.addLayout(teams_buttons_layout)
    
    def load_tournaments(self):
        """Загрузка списка турниров"""
        tournaments = self.team_service.get_all_tournaments()
        
        self.tournament_combo.clear()
        
        if not tournaments:
            self.tournament_combo.addItem("Нет доступных турниров", None)
            self.clear_tournament_info()
            return
        
        for tournament in tournaments:
            self.tournament_combo.addItem(tournament.name, tournament)
        
        # Выбираем первый турнир по умолчанию
        if self.tournament_combo.count() > 0:
            self.tournament_combo.setCurrentIndex(0)
            self.load_tournament_info()
    
    def load_tournament_info(self):
        """Загрузка информации о выбранном турнире"""
        tournament = self.tournament_combo.currentData()
        
        if not tournament:
            self.clear_tournament_info()
            return
        
        self.tournament_name_label.setText(tournament.name)
        
        # Форматирование дат
        start_date = format_date(tournament.start_date) if tournament.start_date else ""
        end_date = format_date(tournament.end_date) if tournament.end_date else ""
        dates = f"{start_date} - {end_date}" if start_date and end_date else ""
        self.tournament_dates_label.setText(dates)
        
        self.tournament_location_label.setText(tournament.location or "")
        self.tournament_description_label.setText(tournament.description or "")
    
    def clear_tournament_info(self):
        """Очистка информации о турнире"""
        self.tournament_name_label.setText("")
        self.tournament_dates_label.setText("")
        self.tournament_location_label.setText("")
        self.tournament_description_label.setText("")
        self.teams_table.setRowCount(0)
    
    def load_teams(self):
        """Загрузка списка команд-участников турнира"""
        tournament = self.tournament_combo.currentData()
        
        if not tournament:
            self.teams_table.setRowCount(0)
            return
        
        # Обновляем информацию о турнире
        self.load_tournament_info()
        
        # Загружаем список команд
        tournament_teams = self.team_service.get_tournament_teams(tournament.id)
        
        self.teams_table.setRowCount(0)
        for row, tt in enumerate(tournament_teams):
            self.teams_table.insertRow(row)
            
            self.teams_table.setItem(row, 0, QTableWidgetItem(str(tt.id)))
            
            team_name = tt.team.name if tt.team else ""
            self.teams_table.setItem(row, 1, QTableWidgetItem(team_name))
            
            rank = str(tt.rank) if tt.rank else ""
            self.teams_table.setItem(row, 2, QTableWidgetItem(rank))
            
            # В будущем можно добавить примечания
            self.teams_table.setItem(row, 3, QTableWidgetItem(""))
    
    def manage_tournaments(self):
        """Управление турнирами"""
        # В будущем здесь будет вызов диалога управления турнирами
        QMessageBox.information(self, "Информация", "Функция управления турнирами будет доступна в следующей версии")
    
    def add_tournament(self):
        """Добавление нового турнира"""
        dialog = TournamentDialog(parent=self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            self.load_tournaments()
            show_info_message(self, "Информация", "Турнир успешно добавлен")
    
    def add_team(self):
        """Добавление команды в турнир"""
        tournament = self.tournament_combo.currentData()
        
        if not tournament:
            show_error_message(self, "Ошибка", "Сначала выберите турнир")
            return
        
        dialog = AddTeamToTournamentDialog(tournament.id, parent=self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            self.load_teams()
            show_info_message(self, "Информация", "Команда успешно добавлена в турнир")
    
    def remove_team(self):
        """Удаление команды из турнира"""
        selected_rows = self.teams_table.selectedItems()
        if not selected_rows:
            show_error_message(self, "Ошибка", "Выберите команду для удаления из турнира")
            return
        
        tournament_team_id = int(self.teams_table.item(selected_rows[0].row(), 0).text())
        team_name = self.teams_table.item(selected_rows[0].row(), 1).text()
        
        if not show_question_message(self, "Подтверждение", f"Вы действительно хотите удалить команду '{team_name}' из турнира?"):
            return
        
        try:
            self.team_service.remove_team_from_tournament(tournament_team_id)
            self.load_teams()
            show_info_message(self, "Информация", "Команда успешно удалена из турнира")
        except Exception as e:
            show_error_message(self, "Ошибка", f"Не удалось удалить команду из турнира: {str(e)}")
    
    def update_rank(self):
        """Обновление места команды в турнире"""
        selected_rows = self.teams_table.selectedItems()
        if not selected_rows:
            show_error_message(self, "Ошибка", "Выберите команду для обновления места в турнире")
            return
        
        tournament_team_id = int(self.teams_table.item(selected_rows[0].row(), 0).text())
        team_name = self.teams_table.item(selected_rows[0].row(), 1).text()
        current_rank = self.teams_table.item(selected_rows[0].row(), 2).text()
        
        # Простой диалог для ввода места
        dialog = QDialog(self)
        dialog.setWindowTitle("Обновление места в турнире")
        layout = QFormLayout(dialog)
        
        rank_spin = QSpinBox()
        rank_spin.setMinimum(1)
        rank_spin.setMaximum(100)
        if current_rank:
            rank_spin.setValue(int(current_rank))
        else:
            rank_spin.setValue(1)
        
        layout.addRow(f"Место команды '{team_name}':", rank_spin)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            try:
                self.team_service.update_team_rank(tournament_team_id, rank_spin.value())
                self.load_teams()
                show_info_message(self, "Информация", "Место команды в турнире успешно обновлено")
            except Exception as e:
                show_error_message(self, "Ошибка", f"Не удалось обновить место команды: {str(e)}")
    
    def export_to_excel(self):
        """Экспорт списка команд-участников в Excel"""
        tournament = self.tournament_combo.currentData()
        
        if not tournament:
            show_error_message(self, "Ошибка", "Сначала выберите турнир")
            return
        
        try:
            # Получаем данные из таблицы
            data = []
            headers = ["Команда", "Место в турнире", "Примечания"]
            
            for row in range(self.teams_table.rowCount()):
                row_data = {}
                for col in range(1, self.teams_table.columnCount()):
                    row_data[headers[col-1]] = self.teams_table.item(row, col).text()
                data.append(row_data)
            
            # Экспорт в Excel
            filename = f"Команды_турнира_{tournament.name}.xlsx"
            filepath = export_to_excel(data, filename, "Команды")
            show_info_message(self, "Экспорт", f"Данные успешно экспортированы в файл:\n{filepath}")
        except Exception as e:
            show_error_message(self, "Ошибка", f"Не удалось экспортировать данные: {str(e)}")

