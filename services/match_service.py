# -*- coding: utf-8 -*-

"""
Сервис для работы с матчами
"""

from datetime import date, timedelta
from sqlalchemy import and_, or_, func

from database import get_session
from models import Match, Team, PlayerStats, TeamStats, Video

class MatchService:
    """Сервис для работы с матчами"""
    
    def __init__(self):
        """Инициализация сервиса"""
        self.session = get_session()
    
    def get_matches(self, team_id=None, start_date=None, end_date=None, status=None):
        """
        Получение списка матчей с возможностью фильтрации
        
        Args:
            team_id (int, optional): ID команды для фильтрации. Defaults to None.
            start_date (date, optional): Начальная дата. Defaults to None.
            end_date (date, optional): Конечная дата. Defaults to None.
            status (str, optional): Статус матча (запланирован, завершен, отменен). Defaults to None.
            
        Returns:
            list: Список матчей, соответствующих фильтрам
        """
        try:
            query = self.session.query(Match)
            
            # Применение фильтров
            if team_id:
                query = query.filter(
                    or_(
                        Match.home_team_id == team_id,
                        Match.away_team_id == team_id
                    )
                )
            
            if start_date:
                query = query.filter(Match.date >= start_date)
            
            if end_date:
                query = query.filter(Match.date <= end_date)
            
            if status:
                query = query.filter(Match.status == status)
            
            # Сортировка по дате и времени
            query = query.order_by(Match.date, Match.time)
            
            return query.all()
        except Exception as e:
            print(f"Ошибка при получении списка матчей: {str(e)}")
            return []
    
    def get_upcoming_matches(self, days=30):
        """
        Получение списка предстоящих матчей
        
        Args:
            days (int, optional): Количество дней вперед. Defaults to 30.
            
        Returns:
            list: Список предстоящих матчей
        """
        try:
            today = date.today()
            end_date = today + timedelta(days=days)
            
            return self.session.query(Match).filter(
                and_(
                    Match.date >= today,
                    Match.date <= end_date,
                    Match.status == "запланирован"
                )
            ).order_by(Match.date, Match.time).all()
        except Exception as e:
            print(f"Ошибка при получении предстоящих матчей: {str(e)}")
            return []
    
    def get_past_matches(self, days=30):
        """
        Получение списка прошедших матчей
        
        Args:
            days (int, optional): Количество дней назад. Defaults to 30.
            
        Returns:
            list: Список прошедших матчей
        """
        try:
            today = date.today()
            start_date = today - timedelta(days=days)
            
            return self.session.query(Match).filter(
                and_(
                    Match.date >= start_date,
                    Match.date <= today,
                    Match.status == "завершен"
                )
            ).order_by(Match.date.desc(), Match.time.desc()).all()
        except Exception as e:
            print(f"Ошибка при получении прошедших матчей: {str(e)}")
            return []
    
    def get_match_by_id(self, match_id):
        """
        Получение матча по ID
        
        Args:
            match_id (int): ID матча
            
        Returns:
            Match: Объект матча или None, если матч не найден
        """
        try:
            return self.session.query(Match).filter(Match.id == match_id).first()
        except Exception as e:
            print(f"Ошибка при получении матча: {str(e)}")
            return None
    
    def create_match(self, match_data):
        """
        Создание нового матча
        
        Args:
            match_data (dict): Данные матча
            
        Returns:
            Match: Созданный матч или None в случае ошибки
        """
        try:
            # Создание нового матча
            match = Match(
                date=match_data.get('date'),
                time=match_data.get('time'),
                home_team_id=match_data.get('home_team_id'),
                away_team_id=match_data.get('away_team_id'),
                location=match_data.get('location'),
                status=match_data.get('status', "запланирован"),
                notes=match_data.get('notes')
            )
            
            # Сохранение матча
            self.session.add(match)
            self.session.commit()
            
            return match
        except Exception as e:
            print(f"Ошибка при создании матча: {str(e)}")
            self.session.rollback()
            return None
    
    def update_match(self, match_id, match_data):
        """
        Обновление данных матча
        
        Args:
            match_id (int): ID матча
            match_data (dict): Новые данные матча
            
        Returns:
            Match: Обновленный матч или None в случае ошибки
        """
        try:
            # Поиск матча
            match = self.session.query(Match).filter(Match.id == match_id).first()
            
            if not match:
                return None
            
            # Обновление данных
            match.date = match_data.get('date', match.date)
            match.time = match_data.get('time', match.time)
            match.home_team_id = match_data.get('home_team_id', match.home_team_id)
            match.away_team_id = match_data.get('away_team_id', match.away_team_id)
            match.location = match_data.get('location', match.location)
            match.home_score = match_data.get('home_score', match.home_score)
            match.away_score = match_data.get('away_score', match.away_score)
            match.status = match_data.get('status', match.status)
            match.notes = match_data.get('notes', match.notes)
            match.video_path = match_data.get('video_path', match.video_path)
            
            self.session.commit()
            
            return match
        except Exception as e:
            print(f"Ошибка при обновлении матча: {str(e)}")
            self.session.rollback()
            return None
    
    def delete_match(self, match_id):
        """
        Удаление матча
        
        Args:
            match_id (int): ID матча
            
        Returns:
            bool: True при успешном удалении, False в противном случае
        """
        try:
            # Поиск матча
            match = self.session.query(Match).filter(Match.id == match_id).first()
            
            if not match:
                return False
            
            # Удаление связанных записей статистики игроков
            self.session.query(PlayerStats).filter(PlayerStats.match_id == match_id).delete()
            
            # Удаление связанных записей статистики команд
            self.session.query(TeamStats).filter(TeamStats.match_id == match_id).delete()
            
            # Удаление матча
            self.session.delete(match)
            self.session.commit()
            
            return True
        except Exception as e:
            print(f"Ошибка при удалении матча: {str(e)}")
            self.session.rollback()
            return False
    
    def update_match_result(self, match_id, home_score, away_score, status="завершен"):
        """
        Обновление результата матча
        
        Args:
            match_id (int): ID матча
            home_score (int): Счет домашней команды
            away_score (int): Счет гостевой команды
            status (str, optional): Статус матча. Defaults to "завершен".
            
        Returns:
            Match: Обновленный матч или None в случае ошибки
        """
        try:
            # Поиск матча
            match = self.session.query(Match).filter(Match.id == match_id).first()
            
            if not match:
                return None
            
            # Обновление результата
            match.home_score = home_score
            match.away_score = away_score
            match.status = status
            
            self.session.commit()
            
            return match
        except Exception as e:
            print(f"Ошибка при обновлении результата матча: {str(e)}")
            self.session.rollback()
            return None
    
    def get_match_videos(self, match_id):
        """
        Получение видеоматериалов, связанных с матчем
        
        Args:
            match_id (int): ID матча
            
        Returns:
            list: Список видеоматериалов
        """
        try:
            videos = self.session.query(Video).filter(Video.match_id == match_id).all()
            
            result = []
            for video in videos:
                result.append({
                    'id': video.id,
                    'title': video.title,
                    'file_path': video.file_path,
                    'uploaded_at': video.uploaded_at,
                    'description': video.description
                })
            
            return result
        except Exception as e:
            print(f"Ошибка при получении видеоматериалов: {str(e)}")
            return []
    
    def get_match_count(self, team_id=None):
        """
        Получение количества матчей
        
        Args:
            team_id (int, optional): ID команды для фильтрации. Defaults to None.
            
        Returns:
            int: Количество матчей
        """
        try:
            query = self.session.query(func.count(Match.id))
            
            if team_id:
                query = query.filter(
                    or_(
                        Match.home_team_id == team_id,
                        Match.away_team_id == team_id
                    )
                )
            
            return query.scalar() or 0
        except Exception as e:
            print(f"Ошибка при подсчете матчей: {str(e)}")
            return 0
    
    def get_team_record(self, team_id):
        """
        Получение статистики побед/поражений команды
        
        Args:
            team_id (int): ID команды
            
        Returns:
            dict: Статистика побед/поражений
        """
        try:
            # Получаем все завершенные матчи команды
            matches = self.session.query(Match).filter(
                or_(
                    Match.home_team_id == team_id,
                    Match.away_team_id == team_id
                ),
                Match.status == "завершен"
            ).all()
            
            wins = 0
            losses = 0
            
            for match in matches:
                if match.home_team_id == team_id:
                    if match.home_score > match.away_score:
                        wins += 1
                    else:
                        losses += 1
                else:  # away_team_id == team_id
                    if match.away_score > match.home_score:
                        wins += 1
                    else:
                        losses += 1
            
            return {
                'wins': wins,
                'losses': losses,
                'total': wins + losses,
                'win_percentage': (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
            }
        except Exception as e:
            print(f"Ошибка при получении статистики команды: {str(e)}")
            return {
                'wins': 0,
                'losses': 0,
                'total': 0,
                'win_percentage': 0
            }
    
    def add_match_video(self, match_id, video_data):
        """
        Добавление видео к матчу
        
        Args:
            match_id (int): ID матча
            video_data (dict): Данные видео
            
        Returns:
            Video: Созданное видео или None в случае ошибки
        """
        try:
            # Поиск матча
            match = self.session.query(Match).filter(Match.id == match_id).first()
            
            if not match:
                return None
            
            # Создание видео
            video = Video(
                title=video_data.get('title'),
                file_path=video_data.get('file_path'),
                uploaded_at=video_data.get('uploaded_at'),
                description=video_data.get('description'),
                type="матч",
                match_id=match_id
            )
            
            # Сохранение видео
            self.session.add(video)
            self.session.commit()
            
            return video
        except Exception as e:
            print(f"Ошибка при добавлении видео к матчу: {str(e)}")
            self.session.rollback()
            return None