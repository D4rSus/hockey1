# -*- coding: utf-8 -*-

"""
Виджет для отображения статистики команды
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QTableWidget, QTableWidgetItem, QHeaderView, 
                           QComboBox, QLabel, QMessageBox, QTabWidget,
                           QGridLayout, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from services.stats_service import StatsService
from services.team_service import TeamService
from utils import (show_error_message, show_info_message, 
                  export_to_excel, generate_chart)

class TeamStatsWidget(QWidget):
    """Виджет для отображения статистики команды"""
    
    def __init__(self):
        super().__init__()
        
        self.stats_service = StatsService()
        self.team_service = TeamService()
        
        self.init_ui()
        self.load_teams()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout(self)
        
        # Панель фильтров
        filter_layout = QHBoxLayout()
        
        # Выбор команды
        filter_layout.addWidget(QLabel("Команда:"))
        self.team_combo = QComboBox()
        self.team_combo.currentIndexChanged.connect(self.load_stats)
        filter_layout.addWidget(self.team_combo)
        
        filter_layout.addStretch()
        
        # Кнопки действий
        export_button = QPushButton("Экспорт в Excel")
        export_button.clicked.connect(self.export_to_excel)
        filter_layout.addWidget(export_button)
        
        layout.addLayout(filter_layout)
        
        # Вкладки статистики
        self.tabs = QTabWidget()
        
        # Вкладка с общей статистикой команды
        self.team_tab = QWidget()
        team_layout = QVBoxLayout(self.team_tab)
        
        # Основные показатели команды
        stats_group = QGroupBox("Основные показатели")
        stats_grid = QGridLayout(stats_group)
        
        self.games_label = QLabel("0")
        stats_grid.addWidget(QLabel("Игр:"), 0, 0)
        stats_grid.addWidget(self.games_label, 0, 1)
        
        self.wins_label = QLabel("0")
        stats_grid.addWidget(QLabel("Победы:"), 0, 2)
        stats_grid.addWidget(self.wins_label, 0, 3)
        
        self.losses_label = QLabel("0")
        stats_grid.addWidget(QLabel("Поражения:"), 0, 4)
        stats_grid.addWidget(self.losses_label, 0, 5)
        
        self.goals_for_label = QLabel("0")
        stats_grid.addWidget(QLabel("Забито голов:"), 1, 0)
        stats_grid.addWidget(self.goals_for_label, 1, 1)
        
        self.goals_against_label = QLabel("0")
        stats_grid.addWidget(QLabel("Пропущено голов:"), 1, 2)
        stats_grid.addWidget(self.goals_against_label, 1, 3)
        
        self.goal_diff_label = QLabel("0")
        stats_grid.addWidget(QLabel("Разница:"), 1, 4)
        stats_grid.addWidget(self.goal_diff_label, 1, 5)
        
        team_layout.addWidget(stats_group)
        
        # Таблица матчей
        self.matches_table = QTableWidget()
        self.matches_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.matches_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.matches_table.setColumnCount(6)
        self.matches_table.setHorizontalHeaderLabels([
            "Дата", "Соперник", "Счет", "Голы", "Пропущено", "Результат"
        ])
        self.matches_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        team_layout.addWidget(QLabel("Результаты матчей:"))
        team_layout.addWidget(self.matches_table)
        
        # Графики
        charts_layout = QHBoxLayout()
        
        # Создание места для графиков
        self.goals_chart_container = QWidget()
        goals_chart_layout = QVBoxLayout(self.goals_chart_container)
        goals_chart_layout.addWidget(QLabel("Динамика голов"))
        self.goals_chart_widget = QWidget()
        goals_chart_layout.addWidget(self.goals_chart_widget)
        charts_layout.addWidget(self.goals_chart_container)
        
        self.results_chart_container = QWidget()
        results_chart_layout = QVBoxLayout(self.results_chart_container)
        results_chart_layout.addWidget(QLabel("Результаты матчей"))
        self.results_chart_widget = QWidget()
        results_chart_layout.addWidget(self.results_chart_widget)
        charts_layout.addWidget(self.results_chart_container)
        
        team_layout.addLayout(charts_layout)
        
        self.tabs.addTab(self.team_tab, "Статистика команды")
        
        # Вкладка со статистикой игроков команды
        self.players_tab = QWidget()
        players_layout = QVBoxLayout(self.players_tab)
        
        self.players_table = QTableWidget()
        self.players_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.players_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.players_table.setColumnCount(9)
        self.players_table.setHorizontalHeaderLabels([
            "Игрок", "Амплуа", "Игр", "Голы", "Передачи", "Очки", "+/-", "Штраф. мин.", "Бросков"
        ])
        self.players_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        players_layout.addWidget(self.players_table)
        
        # Кнопка сравнения игроков
        compare_button = QPushButton("Сравнить игроков")
        compare_button.clicked.connect(self.compare_players)
        players_layout.addWidget(compare_button)
        
        self.tabs.addTab(self.players_tab, "Статистика игроков")
        
        layout.addWidget(self.tabs)
    
    def load_teams(self):
        """Загрузка списка команд"""
        teams = self.team_service.get_all_teams()
        
        self.team_combo.clear()
        for team in teams:
            self.team_combo.addItem(team.name, team.id)
    
    def load_stats(self):
        """Загрузка статистики выбранной команды"""
        team_id = self.team_combo.currentData()
        if not team_id:
            return
        
        # Загрузка основных показателей
        team_stats = self.stats_service.get_team_stats(team_id)
        
        self.games_label.setText(str(team_stats.get('games', 0)))
        self.wins_label.setText(str(team_stats.get('wins', 0)))
        self.losses_label.setText(str(team_stats.get('losses', 0)))
        self.goals_for_label.setText(str(team_stats.get('goals_for', 0)))
        self.goals_against_label.setText(str(team_stats.get('goals_against', 0)))
        
        # Расчет разности голов
        goals_for = team_stats.get('goals_for', 0)
        goals_against = team_stats.get('goals_against', 0)
        goal_diff = goals_for - goals_against
        self.goal_diff_label.setText(str(goal_diff))
        
        # Загрузка результатов матчей
        matches = self.stats_service.get_team_matches(team_id)
        
        self.matches_table.setRowCount(0)
        for row, match in enumerate(matches):
            self.matches_table.insertRow(row)
            
            self.matches_table.setItem(row, 0, QTableWidgetItem(match['date']))
            self.matches_table.setItem(row, 1, QTableWidgetItem(match['opponent']))
            self.matches_table.setItem(row, 2, QTableWidgetItem(match['score']))
            self.matches_table.setItem(row, 3, QTableWidgetItem(str(match['goals_for'])))
            self.matches_table.setItem(row, 4, QTableWidgetItem(str(match['goals_against'])))
            self.matches_table.setItem(row, 5, QTableWidgetItem(match['result']))
            
            # Установка цвета для результата
            result_item = self.matches_table.item(row, 5)
            if match['result'] == 'Победа':
                result_item.setBackground(Qt.green)
            elif match['result'] == 'Поражение':
                result_item.setBackground(Qt.red)
            else:
                result_item.setBackground(Qt.yellow)
        
        # Загрузка статистики игроков
        players_stats = self.stats_service.get_team_players_stats(team_id)
        
        self.players_table.setRowCount(0)
        for row, player in enumerate(players_stats):
            self.players_table.insertRow(row)
            
            self.players_table.setItem(row, 0, QTableWidgetItem(player['name']))
            self.players_table.setItem(row, 1, QTableWidgetItem(player['position']))
            self.players_table.setItem(row, 2, QTableWidgetItem(str(player['games'])))
            self.players_table.setItem(row, 3, QTableWidgetItem(str(player['goals'])))
            self.players_table.setItem(row, 4, QTableWidgetItem(str(player['assists'])))
            self.players_table.setItem(row, 5, QTableWidgetItem(str(player['points'])))
            self.players_table.setItem(row, 6, QTableWidgetItem(str(player['plus_minus'])))
            self.players_table.setItem(row, 7, QTableWidgetItem(str(player['penalty_minutes'])))
            self.players_table.setItem(row, 8, QTableWidgetItem(str(player['shots'])))
        
        # Создание графиков
        self.create_goals_chart(matches)
        self.create_results_chart(team_stats)
    
    def create_goals_chart(self, matches):
        """Создание графика динамики голов"""
        # Очистка контейнера графика
        layout = self.goals_chart_widget.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        else:
            layout = QVBoxLayout(self.goals_chart_widget)
        
        # Создание графика, если есть данные
        if matches:
            fig = Figure(figsize=(6, 4), dpi=100)
            ax = fig.add_subplot(111)
            
            dates = [match['date'] for match in matches]
            goals_for = [match['goals_for'] for match in matches]
            goals_against = [match['goals_against'] for match in matches]
            
            # Отрисовка графика
            ax.plot(dates, goals_for, 'g-', label='Забито')
            ax.plot(dates, goals_against, 'r-', label='Пропущено')
            
            # Настройка графика
            ax.set_title('Динамика голов')
            ax.set_xlabel('Дата')
            ax.set_ylabel('Количество голов')
            ax.legend()
            
            # Поворот подписей оси X для лучшей читаемости
            for label in ax.get_xticklabels():
                label.set_rotation(45)
                label.set_ha('right')
            
            fig.tight_layout()
            
            # Создание виджета графика
            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)
        else:
            # Сообщение об отсутствии данных
            layout.addWidget(QLabel("Нет данных для построения графика"))
    
    def create_results_chart(self, team_stats):
        """Создание графика результатов матчей"""
        # Очистка контейнера графика
        layout = self.results_chart_widget.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        else:
            layout = QVBoxLayout(self.results_chart_widget)
        
        # Создание графика, если есть данные
        if team_stats:
            wins = team_stats.get('wins', 0)
            losses = team_stats.get('losses', 0)
            
            # Проверяем, есть ли данные для отображения
            if wins > 0 or losses > 0:
                fig = Figure(figsize=(6, 4), dpi=100)
                ax = fig.add_subplot(111)
                
                labels = []
                values = []
                colors = []
                
                if wins > 0:
                    labels.append('Победы')
                    values.append(wins)
                    colors.append('green')
                
                if losses > 0:
                    labels.append('Поражения')
                    values.append(losses)
                    colors.append('red')
                
                # Отрисовка графика только если есть данные
                if values:
                    ax.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
                    
                    fig.tight_layout()
                    
                    # Создание виджета графика
                    canvas = FigureCanvas(fig)
                    layout.addWidget(canvas)
                else:
                    layout.addWidget(QLabel("Нет данных для построения графика"))
            else:
                # Сообщение об отсутствии данных
                layout.addWidget(QLabel("Нет данных для построения графика"))
        else:
            # Сообщение об отсутствии данных
            layout.addWidget(QLabel("Нет данных для построения графика"))
    
    def compare_players(self):
        """Сравнение выбранных игроков"""
        # Получение выбранных строк
        selected_rows = self.players_table.selectedItems()
        
        if not selected_rows or len(set(item.row() for item in selected_rows)) < 2:
            show_error_message(self, "Ошибка", "Выберите хотя бы двух игроков для сравнения")
            return
        
        # В будущем здесь будет вызов диалога сравнения игроков
        QMessageBox.information(self, "Информация", "Функция сравнения игроков будет доступна в следующей версии")
    
    def export_to_excel(self):
        """Экспорт статистики в Excel"""
        try:
            current_tab = self.tabs.currentIndex()
            
            if current_tab == 0:  # Статистика команды
                # Экспорт результатов матчей
                data = []
                for row in range(self.matches_table.rowCount()):
                    row_data = {}
                    for col in range(self.matches_table.columnCount()):
                        row_data[self.matches_table.horizontalHeaderItem(col).text()] = self.matches_table.item(row, col).text()
                    data.append(row_data)
                
                filepath = export_to_excel(data, "Статистика_команды.xlsx", "Матчи")
            else:  # Статистика игроков
                # Экспорт статистики игроков
                data = []
                for row in range(self.players_table.rowCount()):
                    row_data = {}
                    for col in range(self.players_table.columnCount()):
                        row_data[self.players_table.horizontalHeaderItem(col).text()] = self.players_table.item(row, col).text()
                    data.append(row_data)
                
                filepath = export_to_excel(data, "Статистика_игроков.xlsx", "Игроки")
            
            show_info_message(self, "Экспорт", f"Данные успешно экспортированы в файл:\n{filepath}")
        except Exception as e:
            show_error_message(self, "Ошибка", f"Не удалось экспортировать данные: {str(e)}")
