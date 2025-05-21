# -*- coding: utf-8 -*-

"""
Сервис для работы со статистикой игроков и команд
"""

from sqlalchemy import func, and_, or_, desc
from sqlalchemy.sql.expression import cast
from sqlalchemy.types import Integer
from datetime import datetime, date, timedelta

from database import get_session
from models import PlayerStats, TeamStats, Player, Team, Match

class StatsService:
    """Сервис для работы со статистикой"""
    
    def __init__(self):
        """Инициализация сервиса"""
        self.session = get_session()
    
    def get_player_stats(self, player_id, start_date=None, end_date=None):
        """
        Получение статистики игрока
        
        Args:
            player_id (int): ID игрока
            start_date (date, optional): Начальная дата. Defaults to None.
            end_date (date, optional): Конечная дата. Defaults to None.
            
        Returns:
            dict: Статистика игрока
        """
        try:
            query = self.session.query(
                func.sum(PlayerStats.goals).label('goals'),
                func.sum(PlayerStats.assists).label('assists'),
                func.sum(PlayerStats.penalty_minutes).label('penalty_minutes'),
                func.sum(PlayerStats.plus_minus).label('plus_minus'),
                func.sum(PlayerStats.shots).label('shots'),
                func.sum(PlayerStats.time_on_ice).label('time_on_ice'),
                func.sum(PlayerStats.faceoffs_won).label('faceoffs_won'),
                func.sum(PlayerStats.faceoffs_total).label('faceoffs_total')
            ).filter(PlayerStats.player_id == player_id)
            
            # Применение фильтров по дате
            if start_date or end_date:
                query = query.join(Match, PlayerStats.match_id == Match.id)
                
                if start_date:
                    query = query.filter(Match.date >= start_date)
                
                if end_date:
                    query = query.filter(Match.date <= end_date)
            
            result = query.first()
            
            # Проверяем, что результат не None
            if result is None:
                stats = {
                    'goals': 0,
                    'assists': 0,
                    'penalty_minutes': 0,
                    'plus_minus': 0,
                    'shots': 0,
                    'time_on_ice': 0,
                    'faceoffs_won': 0,
                    'faceoffs_total': 0
                }
            else:
                # Формирование результата
                stats = {
                    'goals': 0 if result.goals is None else result.goals,
                    'assists': 0 if result.assists is None else result.assists,
                    'penalty_minutes': 0 if result.penalty_minutes is None else result.penalty_minutes,
                    'plus_minus': 0 if result.plus_minus is None else result.plus_minus,
                    'shots': 0 if result.shots is None else result.shots,
                    'time_on_ice': 0 if result.time_on_ice is None else result.time_on_ice,
                    'faceoffs_won': 0 if result.faceoffs_won is None else result.faceoffs_won,
                    'faceoffs_total': 0 if result.faceoffs_total is None else result.faceoffs_total
                }
            
            # Дополнительные расчеты
            stats['points'] = int(stats['goals'] + stats['assists'])
            stats['faceoff_percentage'] = int((stats['faceoffs_won'] / stats['faceoffs_total'] * 100) if stats['faceoffs_total'] > 0 else 0)
            stats['games'] = self.session.query(func.count(PlayerStats.id)).filter(PlayerStats.player_id == player_id).scalar() or 0
            
            return stats
        except Exception as e:
            print(f"Ошибка при получении статистики игрока: {str(e)}")
            return {
                'goals': 0,
                'assists': 0,
                'points': 0,
                'penalty_minutes': 0,
                'plus_minus': 0,
                'shots': 0,
                'time_on_ice': 0,
                'faceoffs_won': 0,
                'faceoffs_total': 0,
                'faceoff_percentage': 0,
                'games': 0
            }
    
    def get_team_stats(self, team_id, start_date=None, end_date=None):
        """
        Получение статистики команды
        
        Args:
            team_id (int): ID команды
            start_date (date, optional): Начальная дата. Defaults to None.
            end_date (date, optional): Конечная дата. Defaults to None.
            
        Returns:
            dict: Статистика команды
        """
        try:
            query = self.session.query(
                func.sum(TeamStats.goals_for).label('goals_for'),
                func.sum(TeamStats.goals_against).label('goals_against'),
                func.sum(TeamStats.shots_for).label('shots_for'),
                func.sum(TeamStats.shots_against).label('shots_against'),
                func.sum(TeamStats.penalty_minutes).label('penalty_minutes'),
                func.sum(TeamStats.powerplay_goals).label('powerplay_goals'),
                func.sum(TeamStats.powerplay_opportunities).label('powerplay_opportunities'),
                func.sum(TeamStats.shorthanded_goals_for).label('shorthanded_goals_for'),
                func.sum(TeamStats.shorthanded_goals_against).label('shorthanded_goals_against')
            ).filter(TeamStats.team_id == team_id)
            
            # Применение фильтров по дате
            if start_date or end_date:
                query = query.join(Match, TeamStats.match_id == Match.id)
                
                if start_date:
                    query = query.filter(Match.date >= start_date)
                
                if end_date:
                    query = query.filter(Match.date <= end_date)
            
            result = query.first()
            
            # Проверяем, что результат не None
            if result is None:
                stats = {
                    'goals_for': 0,
                    'goals_against': 0,
                    'shots_for': 0,
                    'shots_against': 0,
                    'penalty_minutes': 0,
                    'powerplay_goals': 0,
                    'powerplay_opportunities': 0,
                    'shorthanded_goals_for': 0,
                    'shorthanded_goals_against': 0
                }
            else:
                # Формирование результата
                stats = {
                    'goals_for': 0 if result.goals_for is None else result.goals_for,
                    'goals_against': 0 if result.goals_against is None else result.goals_against,
                    'shots_for': 0 if result.shots_for is None else result.shots_for,
                    'shots_against': 0 if result.shots_against is None else result.shots_against,
                    'penalty_minutes': 0 if result.penalty_minutes is None else result.penalty_minutes,
                    'powerplay_goals': 0 if result.powerplay_goals is None else result.powerplay_goals,
                    'powerplay_opportunities': 0 if result.powerplay_opportunities is None else result.powerplay_opportunities,
                    'shorthanded_goals_for': 0 if result.shorthanded_goals_for is None else result.shorthanded_goals_for,
                    'shorthanded_goals_against': 0 if result.shorthanded_goals_against is None else result.shorthanded_goals_against
                }
            
            # Дополнительные расчеты
            stats['powerplay_percentage'] = int((stats['powerplay_goals'] / stats['powerplay_opportunities'] * 100) if stats['powerplay_opportunities'] > 0 else 0)
            stats['games'] = self.get_team_games_count(team_id, start_date, end_date)
            
            # Добавление статистики побед/поражений
            win_loss = self.get_team_win_loss_stats(team_id, start_date, end_date)
            stats.update(win_loss)
            
            return stats
        except Exception as e:
            print(f"Ошибка при получении статистики команды: {str(e)}")
            return {
                'games': 0,
                'wins': 0,
                'losses': 0,
                'win_percentage': 0,
                'goals_for': 0,
                'goals_against': 0,
                'shots_for': 0,
                'shots_against': 0,
                'penalty_minutes': 0,
                'powerplay_goals': 0,
                'powerplay_opportunities': 0,
                'powerplay_percentage': 0,
                'shorthanded_goals_for': 0,
                'shorthanded_goals_against': 0
            }
    
    def get_team_win_loss_stats(self, team_id, start_date=None, end_date=None):
        """
        Получение статистики побед и поражений команды
        
        Args:
            team_id (int): ID команды
            start_date (date, optional): Начальная дата. Defaults to None.
            end_date (date, optional): Конечная дата. Defaults to None.
            
        Returns:
            dict: Статистика побед и поражений
        """
        try:
            # Создание базового запроса для матчей команды
            query = self.session.query(Match).filter(
                or_(
                    Match.home_team_id == team_id,
                    Match.away_team_id == team_id
                )
            ).filter(Match.status == "завершен")
            
            # Применение фильтров по дате
            if start_date:
                query = query.filter(Match.date >= start_date)
            
            if end_date:
                query = query.filter(Match.date <= end_date)
            
            matches = query.all()
            
            wins = 0
            losses = 0
            
            for match in matches:
                # Сравниваем результаты, используя SQLAlchemy-безопасный способ
                is_home = match.home_team_id == team_id
                is_away = match.away_team_id == team_id
                
                # Преобразуем объекты SQLAlchemy в обычные Python-объекты для сравнения
                home_score = match.home_score
                away_score = match.away_score
                
                if home_score is not None and away_score is not None:
                    # Преобразуем к int, но предварительно обеспечиваем, что это не SQLAlchemy-объекты
                    home_score_val = int(home_score) if home_score is not None else 0
                    away_score_val = int(away_score) if away_score is not None else 0
                    
                    if is_home:
                        if home_score_val > away_score_val:
                            wins += 1
                        else:
                            losses += 1
                    elif is_away:
                        if away_score_val > home_score_val:
                            wins += 1
                        else:
                            losses += 1
            
            games = wins + losses
            win_percentage = (wins / games * 100) if games > 0 else 0
            
            return {
                'wins': wins,
                'losses': losses,
                'win_percentage': win_percentage
            }
        except Exception as e:
            print(f"Ошибка при получении статистики побед/поражений: {str(e)}")
            return {
                'wins': 0,
                'losses': 0,
                'win_percentage': 0
            }
    
    def get_team_games_count(self, team_id, start_date=None, end_date=None):
        """
        Получение количества матчей команды
        
        Args:
            team_id (int): ID команды
            start_date (date, optional): Начальная дата. Defaults to None.
            end_date (date, optional): Конечная дата. Defaults to None.
            
        Returns:
            int: Количество матчей
        """
        try:
            query = self.session.query(func.count(Match.id)).filter(
                or_(
                    Match.home_team_id == team_id,
                    Match.away_team_id == team_id
                )
            ).filter(Match.status == "завершен")
            
            # Применение фильтров по дате
            if start_date:
                query = query.filter(Match.date >= start_date)
            
            if end_date:
                query = query.filter(Match.date <= end_date)
            
            return query.scalar() or 0
        except Exception as e:
            print(f"Ошибка при подсчете матчей команды: {str(e)}")
            return 0
    
    def get_top_players(self, team_id=None, category='points', limit=10, start_date=None, end_date=None):
        """
        Получение списка лучших игроков по определенной категории
        
        Args:
            team_id (int, optional): ID команды для фильтрации. Defaults to None.
            category (str, optional): Категория для сортировки. Defaults to 'points'.
            limit (int, optional): Лимит результатов. Defaults to 10.
            start_date (date, optional): Начальная дата. Defaults to None.
            end_date (date, optional): Конечная дата. Defaults to None.
            
        Returns:
            list: Список игроков
        """
        try:
            if category == 'points':
                # Использование суммы голов и передач
                value_query = func.sum(PlayerStats.goals + PlayerStats.assists).label('value')
            elif category == 'goals':
                value_query = func.sum(PlayerStats.goals).label('value')
            elif category == 'assists':
                value_query = func.sum(PlayerStats.assists).label('value')
            elif category == 'penalty_minutes':
                value_query = func.sum(PlayerStats.penalty_minutes).label('value')
            elif category == 'plus_minus':
                value_query = func.sum(PlayerStats.plus_minus).label('value')
            else:
                # По умолчанию используем очки
                value_query = func.sum(PlayerStats.goals + PlayerStats.assists).label('value')
            
            # Базовый запрос
            query = self.session.query(
                Player.id.label('player_id'),
                Player.first_name,
                Player.last_name,
                Player.position,
                Player.team_id,
                Team.name.label('team_name'),
                value_query
            ).join(
                PlayerStats, Player.id == PlayerStats.player_id
            ).join(
                Team, Player.team_id == Team.id
            ).group_by(
                Player.id,
                Team.name
            )
            
            # Фильтрация по команде
            if team_id:
                query = query.filter(Player.team_id == team_id)
            
            # Фильтрация по дате
            if start_date or end_date:
                query = query.join(Match, PlayerStats.match_id == Match.id)
                
                if start_date:
                    query = query.filter(Match.date >= start_date)
                
                if end_date:
                    query = query.filter(Match.date <= end_date)
            
            # Сортировка по убыванию и ограничение результатов
            query = query.order_by(desc('value')).limit(limit)
            
            results = query.all()
            
            # Преобразование результатов в список словарей
            players = []
            for result in results:
                player = {
                    'player_id': result.player_id,
                    'first_name': result.first_name,
                    'last_name': result.last_name,
                    'position': result.position,
                    'team_id': result.team_id,
                    'team_name': result.team_name,
                    'value': result.value or 0
                }
                players.append(player)
            
            return players
        except Exception as e:
            print(f"Ошибка при получении лучших игроков: {str(e)}")
            return []
    
    def get_player_match_stats(self, player_id, match_id):
        """
        Получение статистики игрока в конкретном матче
        
        Args:
            player_id (int): ID игрока
            match_id (int): ID матча
            
        Returns:
            PlayerStats: Объект статистики или None, если статистика не найдена
        """
        try:
            return self.session.query(PlayerStats).filter(
                PlayerStats.player_id == player_id,
                PlayerStats.match_id == match_id
            ).first()
        except Exception as e:
            print(f"Ошибка при получении статистики игрока в матче: {str(e)}")
            return None
    
    def update_player_match_stats(self, player_id, match_id, stats_data):
        """
        Обновление статистики игрока в матче
        
        Args:
            player_id (int): ID игрока
            match_id (int): ID матча
            stats_data (dict): Данные статистики
            
        Returns:
            PlayerStats: Обновленная статистика или None в случае ошибки
        """
        try:
            # Поиск существующей статистики
            stats = self.session.query(PlayerStats).filter(
                PlayerStats.player_id == player_id,
                PlayerStats.match_id == match_id
            ).first()
            
            if stats:
                # Обновление существующей статистики
                stats.goals = stats_data.get('goals', stats.goals)
                stats.assists = stats_data.get('assists', stats.assists)
                stats.penalty_minutes = stats_data.get('penalty_minutes', stats.penalty_minutes)
                stats.plus_minus = stats_data.get('plus_minus', stats.plus_minus)
                stats.shots = stats_data.get('shots', stats.shots)
                stats.time_on_ice = stats_data.get('time_on_ice', stats.time_on_ice)
                stats.faceoffs_won = stats_data.get('faceoffs_won', stats.faceoffs_won)
                stats.faceoffs_total = stats_data.get('faceoffs_total', stats.faceoffs_total)
            else:
                # Создание новой статистики
                stats = PlayerStats(
                    player_id=player_id,
                    match_id=match_id,
                    goals=stats_data.get('goals', 0),
                    assists=stats_data.get('assists', 0),
                    penalty_minutes=stats_data.get('penalty_minutes', 0),
                    plus_minus=stats_data.get('plus_minus', 0),
                    shots=stats_data.get('shots', 0),
                    time_on_ice=stats_data.get('time_on_ice', 0),
                    faceoffs_won=stats_data.get('faceoffs_won', 0),
                    faceoffs_total=stats_data.get('faceoffs_total', 0)
                )
                self.session.add(stats)
            
            self.session.commit()
            
            return stats
        except Exception as e:
            print(f"Ошибка при обновлении статистики игрока: {str(e)}")
            self.session.rollback()
            return None
    
    def get_team_match_stats(self, team_id, match_id):
        """
        Получение статистики команды в конкретном матче
        
        Args:
            team_id (int): ID команды
            match_id (int): ID матча
            
        Returns:
            TeamStats: Объект статистики или None, если статистика не найдена
        """
        try:
            return self.session.query(TeamStats).filter(
                TeamStats.team_id == team_id,
                TeamStats.match_id == match_id
            ).first()
        except Exception as e:
            print(f"Ошибка при получении статистики команды в матче: {str(e)}")
            return None
    
    def update_team_match_stats(self, team_id, match_id, stats_data):
        """
        Обновление статистики команды в матче
        
        Args:
            team_id (int): ID команды
            match_id (int): ID матча
            stats_data (dict): Данные статистики
            
        Returns:
            TeamStats: Обновленная статистика или None в случае ошибки
        """
        try:
            # Поиск существующей статистики
            stats = self.session.query(TeamStats).filter(
                TeamStats.team_id == team_id,
                TeamStats.match_id == match_id
            ).first()
            
            if stats:
                # Обновление существующей статистики
                stats.goals_for = stats_data.get('goals_for', stats.goals_for)
                stats.goals_against = stats_data.get('goals_against', stats.goals_against)
                stats.shots_for = stats_data.get('shots_for', stats.shots_for)
                stats.shots_against = stats_data.get('shots_against', stats.shots_against)
                stats.penalty_minutes = stats_data.get('penalty_minutes', stats.penalty_minutes)
                stats.powerplay_goals = stats_data.get('powerplay_goals', stats.powerplay_goals)
                stats.powerplay_opportunities = stats_data.get('powerplay_opportunities', stats.powerplay_opportunities)
                stats.shorthanded_goals_for = stats_data.get('shorthanded_goals_for', stats.shorthanded_goals_for)
                stats.shorthanded_goals_against = stats_data.get('shorthanded_goals_against', stats.shorthanded_goals_against)
            else:
                # Создание новой статистики
                stats = TeamStats(
                    team_id=team_id,
                    match_id=match_id,
                    goals_for=stats_data.get('goals_for', 0),
                    goals_against=stats_data.get('goals_against', 0),
                    shots_for=stats_data.get('shots_for', 0),
                    shots_against=stats_data.get('shots_against', 0),
                    penalty_minutes=stats_data.get('penalty_minutes', 0),
                    powerplay_goals=stats_data.get('powerplay_goals', 0),
                    powerplay_opportunities=stats_data.get('powerplay_opportunities', 0),
                    shorthanded_goals_for=stats_data.get('shorthanded_goals_for', 0),
                    shorthanded_goals_against=stats_data.get('shorthanded_goals_against', 0)
                )
                self.session.add(stats)
            
            self.session.commit()
            
            return stats
        except Exception as e:
            print(f"Ошибка при обновлении статистики команды: {str(e)}")
            self.session.rollback()
            return None