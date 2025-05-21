# -*- coding: utf-8 -*-

"""
Виджет для составления и просмотра плана тренировок
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                          QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit,
                          QListWidget, QListWidgetItem, QDialog, QFormLayout,
                          QLineEdit, QComboBox, QDialogButtonBox, QGroupBox, QSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal

from models import Training, TrainingExercise
from services.training_service import TrainingService
from ui.dialogs import ExerciseDialog
from utils import show_error_message, show_info_message, show_question_message

class TrainingPlanWidget(QWidget):
    """Виджет для составления и просмотра плана тренировок"""
    
    def __init__(self):
        super().__init__()
        
        self.training_service = TrainingService()
        self.current_training = None
        
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout(self)
        
        # Заголовок
        title_label = QLabel("Составление плана тренировок")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Горизонтальный layout для списков и деталей
        main_layout = QHBoxLayout()
        
        # Левая панель - список тренировок
        left_panel = QGroupBox("Тренировки")
        left_layout = QVBoxLayout(left_panel)
        
        # Список тренировок
        self.trainings_list = QListWidget()
        self.trainings_list.currentItemChanged.connect(self.on_training_selected)
        left_layout.addWidget(self.trainings_list)
        
        # Кнопки для управления тренировками
        trainings_buttons = QHBoxLayout()
        
        self.refresh_button = QPushButton("Обновить список")
        self.refresh_button.clicked.connect(self.load_trainings)
        trainings_buttons.addWidget(self.refresh_button)
        
        left_layout.addLayout(trainings_buttons)
        
        main_layout.addWidget(left_panel, 1)
        
        # Правая панель - детали тренировки и упражнения
        right_panel = QGroupBox("План тренировки")
        right_layout = QVBoxLayout(right_panel)
        
        # Информация о тренировке
        self.training_info = QLabel()
        right_layout.addWidget(self.training_info)
        
        # Список упражнений
        right_layout.addWidget(QLabel("Упражнения:"))
        
        self.exercises_table = QTableWidget()
        self.exercises_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.exercises_table.setSelectionMode(QTableWidget.SingleSelection)
        self.exercises_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.exercises_table.setColumnCount(4)
        self.exercises_table.setHorizontalHeaderLabels([
            "ID", "Порядок", "Название", "Длительность (мин)"
        ])
        self.exercises_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.exercises_table.setColumnHidden(0, True)  # Скрываем ID
        
        right_layout.addWidget(self.exercises_table)
        
        # Описание упражнения
        right_layout.addWidget(QLabel("Описание упражнения:"))
        
        self.exercise_description = QTextEdit()
        self.exercise_description.setReadOnly(True)
        right_layout.addWidget(self.exercise_description)
        
        # Кнопки для управления упражнениями
        exercises_buttons = QHBoxLayout()
        
        self.add_exercise_button = QPushButton("Добавить упражнение")
        self.add_exercise_button.clicked.connect(self.add_exercise)
        exercises_buttons.addWidget(self.add_exercise_button)
        
        self.edit_exercise_button = QPushButton("Редактировать")
        self.edit_exercise_button.clicked.connect(self.edit_exercise)
        exercises_buttons.addWidget(self.edit_exercise_button)
        
        self.delete_exercise_button = QPushButton("Удалить")
        self.delete_exercise_button.clicked.connect(self.delete_exercise)
        exercises_buttons.addWidget(self.delete_exercise_button)
        
        self.move_up_button = QPushButton("Вверх")
        self.move_up_button.clicked.connect(self.move_exercise_up)
        exercises_buttons.addWidget(self.move_up_button)
        
        self.move_down_button = QPushButton("Вниз")
        self.move_down_button.clicked.connect(self.move_exercise_down)
        exercises_buttons.addWidget(self.move_down_button)
        
        right_layout.addLayout(exercises_buttons)
        
        # Изначально отключаем кнопки
        self.disable_exercise_buttons()
        
        main_layout.addWidget(right_panel, 2)
        
        layout.addLayout(main_layout)
        
        # Загрузка списка тренировок
        self.load_trainings()
        
        # Подключение сигнала выбора упражнения
        self.exercises_table.currentItemChanged.connect(self.on_exercise_selected)
    
    def load_trainings(self):
        """Загрузка списка тренировок"""
        self.trainings_list.clear()
        trainings = self.training_service.get_upcoming_trainings()
        
        for training in trainings:
            date_str = training.date.strftime("%d.%m.%Y")
            time_str = training.start_time.strftime("%H:%M") if training.start_time else ""
            team_name = training.team.name if training.team else ""
            
            item_text = f"{date_str} {time_str} - {team_name}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, training)
            
            self.trainings_list.addItem(item)
    
    def on_training_selected(self, current, previous):
        """Обработчик выбора тренировки из списка"""
        if not current:
            self.current_training = None
            self.training_info.setText("Выберите тренировку из списка")
            self.exercises_table.setRowCount(0)
            self.exercise_description.clear()
            self.disable_exercise_buttons()
            return
        
        # Получаем выбранную тренировку
        self.current_training = current.data(Qt.UserRole)
        
        # Отображаем информацию о тренировке
        date_str = self.current_training.date.strftime("%d.%m.%Y") if self.current_training.date else ""
        time_str = ""
        if self.current_training.start_time and self.current_training.end_time:
            start = self.current_training.start_time.strftime("%H:%M")
            end = self.current_training.end_time.strftime("%H:%M")
            time_str = f"{start} - {end}"
        
        team_name = self.current_training.team.name if self.current_training.team else ""
        location = self.current_training.location or ""
        focus_area = self.current_training.focus_area or ""
        
        info_text = f"<b>Дата:</b> {date_str}<br>" \
                    f"<b>Время:</b> {time_str}<br>" \
                    f"<b>Команда:</b> {team_name}<br>" \
                    f"<b>Место:</b> {location}<br>" \
                    f"<b>Направление:</b> {focus_area}"
                    
        self.training_info.setText(info_text)
        
        # Загружаем упражнения
        self.load_exercises()
        
        # Включаем кнопки
        self.add_exercise_button.setEnabled(True)
    
    def load_exercises(self):
        """Загрузка упражнений для выбранной тренировки"""
        if not self.current_training:
            return
        
        # Получаем список упражнений
        exercises = self.training_service.get_training_exercises(self.current_training.id)
        
        # Очищаем таблицу
        self.exercises_table.setRowCount(0)
        
        # Заполняем таблицу
        for row, exercise in enumerate(exercises):
            self.exercises_table.insertRow(row)
            
            self.exercises_table.setItem(row, 0, QTableWidgetItem(str(exercise.id)))
            self.exercises_table.setItem(row, 1, QTableWidgetItem(str(exercise.order)))
            self.exercises_table.setItem(row, 2, QTableWidgetItem(exercise.name))
            
            duration = str(exercise.duration) if exercise.duration else ""
            self.exercises_table.setItem(row, 3, QTableWidgetItem(duration))
    
    def on_exercise_selected(self, current, previous):
        """Обработчик выбора упражнения из таблицы"""
        if not current or not self.current_training:
            self.exercise_description.clear()
            self.disable_exercise_buttons(add_enabled=True)
            return
        
        # Получаем ID выбранного упражнения
        row = current.row()
        exercise_id = int(self.exercises_table.item(row, 0).text())
        
        # Получаем информацию об упражнении
        exercise = self.training_service.get_exercise_by_id(exercise_id)
        
        if exercise:
            # Отображаем описание упражнения
            self.exercise_description.setText(exercise.description or "")
            
            # Включаем кнопки
            self.edit_exercise_button.setEnabled(True)
            self.delete_exercise_button.setEnabled(True)
            
            # Включаем/отключаем кнопки перемещения в зависимости от позиции
            self.move_up_button.setEnabled(row > 0)
            self.move_down_button.setEnabled(row < self.exercises_table.rowCount() - 1)
        else:
            self.exercise_description.clear()
            self.disable_exercise_buttons(add_enabled=True)
    
    def disable_exercise_buttons(self, add_enabled=False):
        """Отключение кнопок управления упражнениями"""
        self.add_exercise_button.setEnabled(add_enabled)
        self.edit_exercise_button.setEnabled(False)
        self.delete_exercise_button.setEnabled(False)
        self.move_up_button.setEnabled(False)
        self.move_down_button.setEnabled(False)
    
    def add_exercise(self):
        """Добавление нового упражнения"""
        if not self.current_training:
            show_error_message(self, "Ошибка", "Сначала выберите тренировку")
            return
        
        # Получаем текущий максимальный порядковый номер
        max_order = 0
        for row in range(self.exercises_table.rowCount()):
            order = int(self.exercises_table.item(row, 1).text())
            max_order = max(max_order, order)
        
        dialog = ExerciseDialog(self.current_training.id, max_order + 1, parent=self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Обновляем список упражнений
            self.load_exercises()
            show_info_message(self, "Информация", "Упражнение успешно добавлено")
    
    def edit_exercise(self):
        """Редактирование выбранного упражнения"""
        selected_rows = self.exercises_table.selectedItems()
        if not selected_rows:
            show_error_message(self, "Ошибка", "Выберите упражнение для редактирования")
            return
        
        exercise_id = int(self.exercises_table.item(selected_rows[0].row(), 0).text())
        exercise = self.training_service.get_exercise_by_id(exercise_id)
        
        if not exercise:
            show_error_message(self, "Ошибка", "Упражнение не найдено")
            return
        
        dialog = ExerciseDialog(self.current_training.id, exercise.order, exercise, parent=self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # Обновляем список упражнений
            self.load_exercises()
            show_info_message(self, "Информация", "Упражнение успешно обновлено")
    
    def delete_exercise(self):
        """Удаление выбранного упражнения"""
        selected_rows = self.exercises_table.selectedItems()
        if not selected_rows:
            show_error_message(self, "Ошибка", "Выберите упражнение для удаления")
            return
        
        exercise_id = int(self.exercises_table.item(selected_rows[0].row(), 0).text())
        
        if not show_question_message(self, "Подтверждение", "Вы действительно хотите удалить выбранное упражнение?"):
            return
        
        try:
            self.training_service.delete_exercise(exercise_id)
            
            # Обновляем список упражнений
            self.load_exercises()
            show_info_message(self, "Информация", "Упражнение успешно удалено")
        except Exception as e:
            show_error_message(self, "Ошибка", f"Не удалось удалить упражнение: {str(e)}")
    
    def move_exercise_up(self):
        """Перемещение упражнения вверх по списку"""
        selected_rows = self.exercises_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        if row <= 0:
            return
        
        exercise_id = int(self.exercises_table.item(row, 0).text())
        prev_exercise_id = int(self.exercises_table.item(row - 1, 0).text())
        
        try:
            # Меняем порядок упражнений
            self.training_service.swap_exercises_order(exercise_id, prev_exercise_id)
            
            # Обновляем список упражнений
            self.load_exercises()
            
            # Выбираем перемещенное упражнение
            self.exercises_table.selectRow(row - 1)
        except Exception as e:
            show_error_message(self, "Ошибка", f"Не удалось переместить упражнение: {str(e)}")
    
    def move_exercise_down(self):
        """Перемещение упражнения вниз по списку"""
        selected_rows = self.exercises_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        if row >= self.exercises_table.rowCount() - 1:
            return
        
        exercise_id = int(self.exercises_table.item(row, 0).text())
        next_exercise_id = int(self.exercises_table.item(row + 1, 0).text())
        
        try:
            # Меняем порядок упражнений
            self.training_service.swap_exercises_order(exercise_id, next_exercise_id)
            
            # Обновляем список упражнений
            self.load_exercises()
            
            # Выбираем перемещенное упражнение
            self.exercises_table.selectRow(row + 1)
        except Exception as e:
            show_error_message(self, "Ошибка", f"Не удалось переместить упражнение: {str(e)}")

