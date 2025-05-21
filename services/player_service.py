# -*- coding: utf-8 -*-

"""
Сервис для работы с игроками
"""

import os
import shutil
from sqlalchemy import or_

from database import get_session
from models import Player, Team, Video
from config import Config
from utils import get_player_photo_path, get_unique_filename

class PlayerService:
    """Сервис для работы с игроками"""
    
    def __init__(self):
        """Инициализация сервиса"""
        self.session = get_session()
    
    def get_players(self, team_id=None, position=None):
        """
        Получение списка игроков с возможностью фильтрации
        
        Args:
            team_id (int, optional): ID команды для фильтрации. Defaults to None.
            position (str, optional): Амплуа для фильтрации. Defaults to None.
            
        Returns:
            list: Список игроков, соответствующих фильтрам
        """
        try:
            query = self.session.query(Player).filter(Player.is_active == True)
            
            if team_id:
                query = query.filter(Player.team_id == team_id)
            
            if position:
                query = query.filter(Player.position == position)
            
            # Сортировка по фамилии, имени
            query = query.order_by(Player.last_name, Player.first_name)
            
            return query.all()
        except Exception as e:
            print(f"Ошибка при получении списка игроков: {str(e)}")
            return []
    
    def search_players(self, search_term):
        """
        Поиск игроков по имени или фамилии
        
        Args:
            search_term (str): Поисковый запрос
            
        Returns:
            list: Список найденных игроков
        """
        try:
            # Формирование поискового запроса
            search = f"%{search_term}%"
            
            # Поиск по имени или фамилии
            query = self.session.query(Player).filter(
                or_(
                    Player.first_name.ilike(search),
                    Player.last_name.ilike(search),
                    Player.middle_name.ilike(search)
                )
            ).filter(Player.is_active == True)
            
            # Сортировка по фамилии, имени
            query = query.order_by(Player.last_name, Player.first_name)
            
            return query.all()
        except Exception as e:
            print(f"Ошибка при поиске игроков: {str(e)}")
            return []
    
    def get_player_by_id(self, player_id):
        """
        Получение игрока по ID
        
        Args:
            player_id (int): ID игрока
            
        Returns:
            Player: Объект игрока или None, если игрок не найден
        """
        try:
            return self.session.query(Player).filter(Player.id == player_id).first()
        except Exception as e:
            print(f"Ошибка при получении игрока: {str(e)}")
            return None
    
    def create_player(self, player_data):
        """
        Создание нового игрока
        
        Args:
            player_data (dict): Данные игрока
            
        Returns:
            Player: Созданный игрок или None в случае ошибки
        """
        try:
            # Создание нового игрока
            player = Player(
                first_name=player_data.get('first_name'),
                last_name=player_data.get('last_name'),
                middle_name=player_data.get('middle_name'),
                birth_date=player_data.get('birth_date'),
                position=player_data.get('position'),
                jersey_number=player_data.get('jersey_number'),
                height=player_data.get('height'),
                weight=player_data.get('weight'),
                team_id=player_data.get('team_id'),
                notes=player_data.get('notes'),
                is_active=True
            )
            
            # Обработка фотографии
            photo_path = player_data.get('photo_path')
            if photo_path:
                player.photo_path = self._process_photo(photo_path, player.id)
            
            # Сохранение игрока
            self.session.add(player)
            self.session.flush()  # Получаем ID без коммита
            
            # Если фото было загружено, но ID игрока ещё не был известен
            if photo_path and not player.photo_path:
                player.photo_path = self._process_photo(photo_path, player.id)
            
            self.session.commit()
            
            return player
        except Exception as e:
            print(f"Ошибка при создании игрока: {str(e)}")
            self.session.rollback()
            return None
    
    def update_player(self, player_id, player_data):
        """
        Обновление данных игрока
        
        Args:
            player_id (int): ID игрока
            player_data (dict): Новые данные игрока
            
        Returns:
            Player: Обновленный игрок или None в случае ошибки
        """
        try:
            # Поиск игрока
            player = self.session.query(Player).filter(Player.id == player_id).first()
            
            if not player:
                return None
            
            # Обновление данных
            player.first_name = player_data.get('first_name', player.first_name)
            player.last_name = player_data.get('last_name', player.last_name)
            player.middle_name = player_data.get('middle_name', player.middle_name)
            player.birth_date = player_data.get('birth_date', player.birth_date)
            player.position = player_data.get('position', player.position)
            player.jersey_number = player_data.get('jersey_number', player.jersey_number)
            player.height = player_data.get('height', player.height)
            player.weight = player_data.get('weight', player.weight)
            player.team_id = player_data.get('team_id', player.team_id)
            player.notes = player_data.get('notes', player.notes)
            
            # Обработка фотографии
            photo_path = player_data.get('photo_path')
            if photo_path and photo_path != player.photo_path:
                player.photo_path = self._process_photo(photo_path, player.id)
            
            self.session.commit()
            
            return player
        except Exception as e:
            print(f"Ошибка при обновлении игрока: {str(e)}")
            self.session.rollback()
            return None
    
    def update_player_photo(self, player_id, photo_path):
        """
        Обновление фотографии игрока
        
        Args:
            player_id (int): ID игрока
            photo_path (str): Путь к новой фотографии
            
        Returns:
            bool: True при успешном обновлении, False в противном случае
        """
        try:
            # Поиск игрока
            player = self.session.query(Player).filter(Player.id == player_id).first()
            
            if not player:
                return False
            
            # Обработка фотографии
            if photo_path:
                player.photo_path = self._process_photo(photo_path, player.id)
                self.session.commit()
                return True
            
            return False
        except Exception as e:
            print(f"Ошибка при обновлении фотографии: {str(e)}")
            self.session.rollback()
            return False
    
    def delete_player(self, player_id):
        """
        Удаление игрока (установка флага is_active = False)
        
        Args:
            player_id (int): ID игрока
            
        Returns:
            bool: True при успешном удалении, False в противном случае
        """
        try:
            # Поиск игрока
            player = self.session.query(Player).filter(Player.id == player_id).first()
            
            if not player:
                return False
            
            # Установка флага неактивности вместо удаления
            player.is_active = False
            self.session.commit()
            
            return True
        except Exception as e:
            print(f"Ошибка при удалении игрока: {str(e)}")
            self.session.rollback()
            return False
    
    def _process_photo(self, source_path, player_id):
        """
        Обработка фотографии игрока
        
        Args:
            source_path (str): Исходный путь к фотографии
            player_id (int): ID игрока
            
        Returns:
            str: Путь к сохраненной фотографии или None в случае ошибки
        """
        try:
            # Если player_id не определен, вернем None
            if not player_id:
                return None
            
            # Создание директории для фото игрока
            photo_dir = os.path.join(Config.PHOTOS_DIR, f"player_{player_id}")
            os.makedirs(photo_dir, exist_ok=True)
            
            # Генерация имени файла
            filename = os.path.basename(source_path)
            filename = get_unique_filename(photo_dir, filename)
            
            # Копирование файла
            dest_path = os.path.join(photo_dir, filename)
            shutil.copy2(source_path, dest_path)
            
            return dest_path
        except Exception as e:
            print(f"Ошибка при обработке фотографии: {str(e)}")
            return None
    
    def get_player_videos(self, player_id):
        """
        Получение видеоматериалов, связанных с игроком
        
        Args:
            player_id (int): ID игрока
            
        Returns:
            list: Список видеоматериалов
        """
        try:
            # Получение игрока
            player = self.session.query(Player).filter(Player.id == player_id).first()
            
            if not player:
                return []
            
            # Получение команды игрока
            team_id = player.team_id
            
            # Список для хранения результатов
            videos = []
            
            # Запрос видео тренировок команды
            training_videos = self.session.query(Video).join(
                Video.training
            ).filter(
                Video.training_id.isnot(None),
                Video.training.has(team_id=team_id)
            ).all()
            
            # Запрос видео матчей команды
            match_videos = self.session.query(Video).join(
                Video.match
            ).filter(
                Video.match_id.isnot(None),
                Video.match.has(or_(Match.home_team_id == team_id, Match.away_team_id == team_id))
            ).all()
            
            # Объединение результатов
            for video in training_videos:
                videos.append({
                    'id': video.id,
                    'title': video.title,
                    'date': video.uploaded_at,
                    'type': 'Тренировка',
                    'description': video.description,
                    'file_path': video.file_path
                })
            
            for video in match_videos:
                videos.append({
                    'id': video.id,
                    'title': video.title,
                    'date': video.uploaded_at,
                    'type': 'Матч',
                    'description': video.description,
                    'file_path': video.file_path
                })
            
            # Сортировка по дате (сначала новые)
            videos.sort(key=lambda v: v['date'], reverse=True)
            
            return videos
        except Exception as e:
            print(f"Ошибка при получении видеоматериалов: {str(e)}")
            return []
    
    def add_player_to_team(self, player_id, team_id):
        """
        Добавление игрока в команду
        
        Args:
            player_id (int): ID игрока
            team_id (int): ID команды
            
        Returns:
            bool: True при успешном добавлении, False в противном случае
        """
        try:
            # Поиск игрока
            player = self.session.query(Player).filter(Player.id == player_id).first()
            
            if not player:
                return False
            
            # Обновление команды
            player.team_id = team_id
            self.session.commit()
            
            return True
        except Exception as e:
            print(f"Ошибка при добавлении игрока в команду: {str(e)}")
            self.session.rollback()
            return False
    
    def remove_player_from_team(self, player_id):
        """
        Удаление игрока из команды
        
        Args:
            player_id (int): ID игрока
            
        Returns:
            bool: True при успешном удалении, False в противном случае
        """
        try:
            # Поиск игрока
            player = self.session.query(Player).filter(Player.id == player_id).first()
            
            if not player:
                return False
            
            # Удаление из команды
            player.team_id = None
            self.session.commit()
            
            return True
        except Exception as e:
            print(f"Ошибка при удалении игрока из команды: {str(e)}")
            self.session.rollback()
            return False

