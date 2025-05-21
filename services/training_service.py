# -*- coding: utf-8 -*-

"""
Сервис для работы с тренировками
"""

from datetime import date, timedelta
from sqlalchemy import and_, func

from database import get_session
from models import Training, TrainingExercise, Player, Attendance, Team

class TrainingService:
    """Сервис для работы с тренировками"""
    
    def __init__(self):
        """Инициализация сервиса"""
        self.session = get_session()
    
    def get_trainings(self, team_id=None, start_date=None, end_date=None):
        """
        Получение списка тренировок с возможностью фильтрации
        
        Args:
            team_id (int, optional): ID команды для фильтрации. Defaults to None.
            start_date (date, optional): Начальная дата. Defaults to None.
            end_date (date, optional): Конечная дата. Defaults to None.
            
        Returns:
            list: Список тренировок, соответствующих фильтрам
        """
        try:
            query = self.session.query(Training)
            
            # Применение фильтров
            if team_id:
                query = query.filter(Training.team_id == team_id)
            
            if start_date:
                query = query.filter(Training.date >= start_date)
            
            if end_date:
                query = query.filter(Training.date <= end_date)
            
            # Сортировка по дате и времени
            query = query.order_by(Training.date.desc(), Training.start_time)
            
            return query.all()
        except Exception as e:
            print(f"Ошибка при получении списка тренировок: {str(e)}")
            return []
    
    def get_upcoming_trainings(self, days=30):
        """
        Получение списка предстоящих тренировок
        
        Args:
            days (int, optional): Количество дней вперед. Defaults to 30.
            
        Returns:
            list: Список предстоящих тренировок
        """
        try:
            today = date.today()
            end_date = today + timedelta(days=days)
            
            return self.session.query(Training).filter(
                and_(
                    Training.date >= today,
                    Training.date <= end_date
                )
            ).order_by(Training.date, Training.start_time).all()
        except Exception as e:
            print(f"Ошибка при получении предстоящих тренировок: {str(e)}")
            return []
    
    def get_training_by_id(self, training_id):
        """
        Получение тренировки по ID
        
        Args:
            training_id (int): ID тренировки
            
        Returns:
            Training: Объект тренировки или None, если тренировка не найдена
        """
        try:
            return self.session.query(Training).filter(Training.id == training_id).first()
        except Exception as e:
            print(f"Ошибка при получении тренировки: {str(e)}")
            return None
    
    def create_training(self, training_data):
        """
        Создание новой тренировки
        
        Args:
            training_data (dict): Данные тренировки
            
        Returns:
            Training: Созданная тренировка или None в случае ошибки
        """
        try:
            # Создание новой тренировки
            training = Training(
                date=training_data.get('date'),
                start_time=training_data.get('start_time'),
                end_time=training_data.get('end_time'),
                team_id=training_data.get('team_id'),
                location=training_data.get('location'),
                focus_area=training_data.get('focus_area'),
                description=training_data.get('description')
            )
            
            # Сохранение тренировки
            self.session.add(training)
            self.session.commit()
            
            return training
        except Exception as e:
            print(f"Ошибка при создании тренировки: {str(e)}")
            self.session.rollback()
            return None
    
    def update_training(self, training_id, training_data):
        """
        Обновление данных тренировки
        
        Args:
            training_id (int): ID тренировки
            training_data (dict): Новые данные тренировки
            
        Returns:
            Training: Обновленная тренировка или None в случае ошибки
        """
        try:
            # Поиск тренировки
            training = self.session.query(Training).filter(Training.id == training_id).first()
            
            if not training:
                return None
            
            # Обновление данных
            training.date = training_data.get('date', training.date)
            training.start_time = training_data.get('start_time', training.start_time)
            training.end_time = training_data.get('end_time', training.end_time)
            training.team_id = training_data.get('team_id', training.team_id)
            training.location = training_data.get('location', training.location)
            training.focus_area = training_data.get('focus_area', training.focus_area)
            training.description = training_data.get('description', training.description)
            
            self.session.commit()
            
            return training
        except Exception as e:
            print(f"Ошибка при обновлении тренировки: {str(e)}")
            self.session.rollback()
            return None
    
    def delete_training(self, training_id):
        """
        Удаление тренировки
        
        Args:
            training_id (int): ID тренировки
            
        Returns:
            bool: True при успешном удалении, False в противном случае
        """
        try:
            # Поиск тренировки
            training = self.session.query(Training).filter(Training.id == training_id).first()
            
            if not training:
                return False
            
            # Удаление связанных записей о посещаемости
            self.session.query(Attendance).filter(Attendance.training_id == training_id).delete()
            
            # Удаление связанных упражнений
            self.session.query(TrainingExercise).filter(TrainingExercise.training_id == training_id).delete()
            
            # Удаление тренировки
            self.session.delete(training)
            self.session.commit()
            
            return True
        except Exception as e:
            print(f"Ошибка при удалении тренировки: {str(e)}")
            self.session.rollback()
            return False
    
    def get_training_exercises(self, training_id):
        """
        Получение списка упражнений для тренировки
        
        Args:
            training_id (int): ID тренировки
            
        Returns:
            list: Список упражнений
        """
        try:
            return self.session.query(TrainingExercise).filter(
                TrainingExercise.training_id == training_id
            ).order_by(TrainingExercise.order).all()
        except Exception as e:
            print(f"Ошибка при получении упражнений: {str(e)}")
            return []
    
    def get_exercise_by_id(self, exercise_id):
        """
        Получение упражнения по ID
        
        Args:
            exercise_id (int): ID упражнения
            
        Returns:
            TrainingExercise: Объект упражнения или None, если упражнение не найдено
        """
        try:
            return self.session.query(TrainingExercise).filter(TrainingExercise.id == exercise_id).first()
        except Exception as e:
            print(f"Ошибка при получении упражнения: {str(e)}")
            return None
    
    def create_exercise(self, exercise_data):
        """
        Создание нового упражнения
        
        Args:
            exercise_data (dict): Данные упражнения
            
        Returns:
            TrainingExercise: Созданное упражнение или None в случае ошибки
        """
        try:
            # Создание нового упражнения
            exercise = TrainingExercise(
                training_id=exercise_data.get('training_id'),
                name=exercise_data.get('name'),
                description=exercise_data.get('description'),
                duration=exercise_data.get('duration'),
                order=exercise_data.get('order')
            )
            
            # Сохранение упражнения
            self.session.add(exercise)
            self.session.commit()
            
            return exercise
        except Exception as e:
            print(f"Ошибка при создании упражнения: {str(e)}")
            self.session.rollback()
            return None
    
    def update_exercise(self, exercise_id, exercise_data):
        """
        Обновление данных упражнения
        
        Args:
            exercise_id (int): ID упражнения
            exercise_data (dict): Новые данные упражнения
            
        Returns:
            TrainingExercise: Обновленное упражнение или None в случае ошибки
        """
        try:
            # Поиск упражнения
            exercise = self.session.query(TrainingExercise).filter(TrainingExercise.id == exercise_id).first()
            
            if not exercise:
                return None
            
            # Обновление данных
            exercise.name = exercise_data.get('name', exercise.name)
            exercise.description = exercise_data.get('description', exercise.description)
            exercise.duration = exercise_data.get('duration', exercise.duration)
            exercise.order = exercise_data.get('order', exercise.order)
            
            self.session.commit()
            
            return exercise
        except Exception as e:
            print(f"Ошибка при обновлении упражнения: {str(e)}")
            self.session.rollback()
            return None
    
    def delete_exercise(self, exercise_id):
        """
        Удаление упражнения
        
        Args:
            exercise_id (int): ID упражнения
            
        Returns:
            bool: True при успешном удалении, False в противном случае
        """
        try:
            # Поиск упражнения
            exercise = self.session.query(TrainingExercise).filter(TrainingExercise.id == exercise_id).first()
            
            if not exercise:
                return False
            
            # Удаление упражнения
            self.session.delete(exercise)
            self.session.commit()
            
            return True
        except Exception as e:
            print(f"Ошибка при удалении упражнения: {str(e)}")
            self.session.rollback()
            return False
    
    def swap_exercises_order(self, exercise1_id, exercise2_id):
        """
        Смена порядка упражнений
        
        Args:
            exercise1_id (int): ID первого упражнения
            exercise2_id (int): ID второго упражнения
            
        Returns:
            bool: True при успешной смене, False в противном случае
        """
        try:
            # Поиск упражнений
            exercise1 = self.session.query(TrainingExercise).filter(TrainingExercise.id == exercise1_id).first()
            exercise2 = self.session.query(TrainingExercise).filter(TrainingExercise.id == exercise2_id).first()
            
            if not exercise1 or not exercise2:
                return False
            
            # Смена порядка
            exercise1.order, exercise2.order = exercise2.order, exercise1.order
            
            self.session.commit()
            
            return True
        except Exception as e:
            print(f"Ошибка при смене порядка упражнений: {str(e)}")
            self.session.rollback()
            return False
    
    def get_training_attendance(self, training_id):
        """
        Получение данных о посещаемости тренировки
        
        Args:
            training_id (int): ID тренировки
            
        Returns:
            list: Список записей о посещаемости
        """
        try:
            return self.session.query(Attendance).filter(Attendance.training_id == training_id).all()
        except Exception as e:
            print(f"Ошибка при получении данных о посещаемости: {str(e)}")
            return []
    
    def update_attendance(self, training_id, attendance_data):
        """
        Обновление данных о посещаемости тренировки
        
        Args:
            training_id (int): ID тренировки
            attendance_data (list): Данные о посещаемости
            
        Returns:
            bool: True при успешном обновлении, False в противном случае
        """
        try:
            # Удаление существующих записей
            self.session.query(Attendance).filter(Attendance.training_id == training_id).delete()
            
            # Добавление новых записей
            for data in attendance_data:
                attendance = Attendance(
                    training_id=training_id,
                    player_id=data.get('player_id'),
                    is_present=data.get('is_present', False),
                    reason=data.get('reason')
                )
                self.session.add(attendance)
            
            self.session.commit()
            
            return True
        except Exception as e:
            print(f"Ошибка при обновлении данных о посещаемости: {str(e)}")
            self.session.rollback()
            return False
    
    def get_player_attendance_stats(self, player_id, start_date=None, end_date=None):
        """
        Получение статистики посещаемости игрока
        
        Args:
            player_id (int): ID игрока
            start_date (date, optional): Начальная дата. Defaults to None.
            end_date (date, optional): Конечная дата. Defaults to None.
            
        Returns:
            dict: Статистика посещаемости
        """
        try:
            query = self.session.query(
                func.count(Attendance.id).label('total'),
                func.sum(func.cast(Attendance.is_present, Integer)).label('present')
            ).filter(Attendance.player_id == player_id)
            
            # Применение фильтров по дате
            if start_date or end_date:
                query = query.join(Training, Attendance.training_id == Training.id)
                
                if start_date:
                    query = query.filter(Training.date >= start_date)
                
                if end_date:
                    query = query.filter(Training.date <= end_date)
            
            result = query.first()
            
            total = result.total or 0
            present = result.present or 0
            
            return {
                'total': total,
                'present': present,
                'absent': total - present,
                'percentage': (present / total * 100) if total > 0 else 0
            }
        except Exception as e:
            print(f"Ошибка при получении статистики посещаемости: {str(e)}")
            return {
                'total': 0,
                'present': 0,
                'absent': 0,
                'percentage': 0
            }

