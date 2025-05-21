# -*- coding: utf-8 -*-

"""
Главное окно приложения
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QTabWidget, QMessageBox,
                           QAction, QToolBar, QStatusBar, QMenu)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont

from ui.team_roster import TeamRosterWidget
from ui.player_card import PlayerCardWidget
from ui.team_stats import TeamStatsWidget
from ui.training_schedule import TrainingScheduleWidget
from ui.match_schedule import MatchScheduleWidget
from ui.training_plan import TrainingPlanWidget
from ui.tournament_teams import TournamentTeamsWidget
from utils import show_question_message

class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self, user):
        super().__init__()
        
        self.user = user
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        # Настройка окна
        self.setWindowTitle("Рабочее место тренера хоккейной команды")
        self.setMinimumSize(1024, 768)
        
        # Создание меню
        self.create_menu()
        
        # Создание панели инструментов
        self.create_toolbar()
        
        # Создание статусной строки
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Отображение информации о пользователе
        self.statusBar.showMessage(f"Пользователь: {self.user.full_name}")
        
        # Центральный виджет и его layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Создание вкладок
        self.tab_widget = QTabWidget()
        
        # Добавление вкладок
        self.team_roster_widget = TeamRosterWidget()
        self.tab_widget.addTab(self.team_roster_widget, "Состав команды")
        
        self.player_card_widget = PlayerCardWidget()
        self.tab_widget.addTab(self.player_card_widget, "Карточка игрока")
        
        self.team_stats_widget = TeamStatsWidget()
        self.tab_widget.addTab(self.team_stats_widget, "Статистика команды")
        
        self.training_schedule_widget = TrainingScheduleWidget()
        self.tab_widget.addTab(self.training_schedule_widget, "Расписание тренировок")
        
        self.match_schedule_widget = MatchScheduleWidget()
        self.tab_widget.addTab(self.match_schedule_widget, "Расписание матчей")
        
        self.training_plan_widget = TrainingPlanWidget()
        self.tab_widget.addTab(self.training_plan_widget, "План тренировок")
        
        self.tournament_teams_widget = TournamentTeamsWidget()
        self.tab_widget.addTab(self.tournament_teams_widget, "Команды турнира")
        
        main_layout.addWidget(self.tab_widget)
        
        # Установка связей между виджетами
        self.team_roster_widget.player_selected.connect(self.player_card_widget.load_player)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
    
    def create_menu(self):
        """Создание меню приложения"""
        # Меню "Файл"
        file_menu = self.menuBar().addMenu("Файл")
        
        # Действие "Экспорт"
        export_menu = QMenu("Экспорт", self)
        
        export_roster_action = QAction("Экспорт состава команды", self)
        export_roster_action.triggered.connect(self.export_roster)
        export_menu.addAction(export_roster_action)
        
        export_stats_action = QAction("Экспорт статистики", self)
        export_stats_action.triggered.connect(self.export_stats)
        export_menu.addAction(export_stats_action)
        
        file_menu.addMenu(export_menu)
        
        # Разделитель
        file_menu.addSeparator()
        
        # Действие "Выход"
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню "Команда"
        team_menu = self.menuBar().addMenu("Команда")
        
        # Действие "Добавить игрока"
        add_player_action = QAction("Добавить игрока", self)
        add_player_action.triggered.connect(self.team_roster_widget.add_player)
        team_menu.addAction(add_player_action)
        
        # Действие "Управление командами"
        manage_teams_action = QAction("Управление командами", self)
        manage_teams_action.triggered.connect(self.manage_teams)
        team_menu.addAction(manage_teams_action)
        
        # Меню "Тренировки"
        training_menu = self.menuBar().addMenu("Тренировки")
        
        # Действие "Добавить тренировку"
        add_training_action = QAction("Добавить тренировку", self)
        add_training_action.triggered.connect(self.training_schedule_widget.add_training)
        training_menu.addAction(add_training_action)
        
        # Действие "Отметить посещаемость"
        mark_attendance_action = QAction("Отметить посещаемость", self)
        mark_attendance_action.triggered.connect(self.training_schedule_widget.mark_attendance)
        training_menu.addAction(mark_attendance_action)
        
        # Меню "Матчи"
        match_menu = self.menuBar().addMenu("Матчи")
        
        # Действие "Добавить матч"
        add_match_action = QAction("Добавить матч", self)
        add_match_action.triggered.connect(self.match_schedule_widget.add_match)
        match_menu.addAction(add_match_action)
        
        # Действие "Внести результаты"
        update_results_action = QAction("Внести результаты", self)
        update_results_action.triggered.connect(self.match_schedule_widget.update_match_results)
        match_menu.addAction(update_results_action)
        
        # Меню "Справка"
        help_menu = self.menuBar().addMenu("Справка")
        
        # Действие "О программе"
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Создание панели инструментов"""
        toolbar = QToolBar("Панель инструментов")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        
        # Действие "Добавить игрока"
        add_player_action = QAction("Добавить игрока", self)
        add_player_action.triggered.connect(self.team_roster_widget.add_player)
        toolbar.addAction(add_player_action)
        
        # Действие "Добавить тренировку"
        add_training_action = QAction("Добавить тренировку", self)
        add_training_action.triggered.connect(self.training_schedule_widget.add_training)
        toolbar.addAction(add_training_action)
        
        # Действие "Добавить матч"
        add_match_action = QAction("Добавить матч", self)
        add_match_action.triggered.connect(self.match_schedule_widget.add_match)
        toolbar.addAction(add_match_action)
        
        # Разделитель
        toolbar.addSeparator()
        
        # Действие "Экспорт"
        export_action = QAction("Экспорт данных", self)
        export_action.triggered.connect(self.export_data)
        toolbar.addAction(export_action)
    
    def export_roster(self):
        """Экспорт состава команды"""
        self.team_roster_widget.export_to_excel()
    
    def export_stats(self):
        """Экспорт статистики"""
        self.team_stats_widget.export_to_excel()
    
    def export_data(self):
        """Экспорт данных в зависимости от текущей вкладки"""
        current_index = self.tab_widget.currentIndex()
        
        if current_index == 0:  # Состав команды
            self.team_roster_widget.export_to_excel()
        elif current_index == 2:  # Статистика команды
            self.team_stats_widget.export_to_excel()
        elif current_index == 3:  # Расписание тренировок
            self.training_schedule_widget.export_to_excel()
        elif current_index == 4:  # Расписание матчей
            self.match_schedule_widget.export_to_excel()
    
    def manage_teams(self):
        """Управление командами"""
        # В будущем здесь будет вызов диалога управления командами
        QMessageBox.information(self, "Информация", "Функция управления командами будет доступна в следующей версии")
    
    def show_about(self):
        """Отображение информации о программе"""
        QMessageBox.about(
            self,
            "О программе",
            "Рабочее место тренера хоккейной команды\n\n"
            "Версия 1.0.0\n\n"
            "Программа для автоматизации работы тренера хоккейной команды"
        )
    
    def on_tab_changed(self, index):
        """Обработчик смены вкладки"""
        # Обновление данных на новой вкладке
        if index == 0:  # Состав команды
            self.team_roster_widget.load_players()
        elif index == 2:  # Статистика команды
            self.team_stats_widget.load_stats()
        elif index == 3:  # Расписание тренировок
            self.training_schedule_widget.load_trainings()
        elif index == 4:  # Расписание матчей
            self.match_schedule_widget.load_matches()
        elif index == 6:  # Команды турнира
            self.tournament_teams_widget.load_teams()
    
    def closeEvent(self, event):
        """Обработчик события закрытия окна"""
        if show_question_message(self, "Подтверждение", "Вы действительно хотите выйти из программы?"):
            event.accept()
        else:
            event.ignore()
