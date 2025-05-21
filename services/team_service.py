# -*- coding: utf-8 -*-

"""
Сервис для работы с командами и турнирами
"""

from sqlalchemy import func

from database import get_session
from models import Team, Player, Tournament, TournamentTeam

class TeamService:
    """Сервис для работы с командами и турнирами"""
    
    def __init__(self):
        """Инициализация сервиса"""
        self.session = get_session()
    
    def get_all_teams(self):
        """
        Получение списка всех команд
        
        Returns:
            list: Список команд
        """
        try:
            return self.session.query(Team).order_by(Team.name).all()
        except Exception as e:
            print(f"Ошибка при получении списка команд: {str(e)}")
            return []
    
    def get_team_by_id(self, team_id):
        """
        Получение команды по ID
        
        Args:
            team_id (int): ID команды
            
        Returns:
            Team: Объект команды или None, если команда не найдена
        """
        try:
            return self.session.query(Team).filter(Team.id == team_id).first()
        except Exception as e:
            print(f"Ошибка при получении команды: {str(e)}")
            return None
    
    def create_team(self, team_data):
        """
        Создание новой команды
        
        Args:
            team_data (dict): Данные команды
            
        Returns:
            Team: Созданная команда или None в случае ошибки
        """
        try:
            # Создание новой команды
            team = Team(
                name=team_data.get('name'),
                logo_path=team_data.get('logo_path'),
                description=team_data.get('description'),
                foundation_year=team_data.get('foundation_year'),
                home_arena=team_data.get('home_arena'),
                coach_id=team_data.get('coach_id'),
                is_opponent=team_data.get('is_opponent', False)
            )
            
            # Сохранение команды
            self.session.add(team)
            self.session.commit()
            
            return team
        except Exception as e:
            print(f"Ошибка при создании команды: {str(e)}")
            self.session.rollback()
            return None
    
    def update_team(self, team_id, team_data):
        """
        Обновление данных команды
        
        Args:
            team_id (int): ID команды
            team_data (dict): Новые данные команды
            
        Returns:
            Team: Обновленная команда или None в случае ошибки
        """
        try:
            # Поиск команды
            team = self.session.query(Team).filter(Team.id == team_id).first()
            
            if not team:
                return None
            
            # Обновление данных
            team.name = team_data.get('name', team.name)
            team.logo_path = team_data.get('logo_path', team.logo_path)
            team.description = team_data.get('description', team.description)
            team.foundation_year = team_data.get('foundation_year', team.foundation_year)
            team.home_arena = team_data.get('home_arena', team.home_arena)
            team.coach_id = team_data.get('coach_id', team.coach_id)
            team.is_opponent = team_data.get('is_opponent', team.is_opponent)
            
            self.session.commit()
            
            return team
        except Exception as e:
            print(f"Ошибка при обновлении команды: {str(e)}")
            self.session.rollback()
            return None
    
    def delete_team(self, team_id):
        """
        Удаление команды
        
        Args:
            team_id (int): ID команды
            
        Returns:
            bool: True при успешном удалении, False в противном случае
        """
        try:
            # Поиск команды
            team = self.session.query(Team).filter(Team.id == team_id).first()
            
            if not team:
                return False
            
            # Удаление команды
            self.session.delete(team)
            self.session.commit()
            
            return True
        except Exception as e:
            print(f"Ошибка при удалении команды: {str(e)}")
            self.session.rollback()
            return False
    
    def get_team_count(self):
        """
        Получение количества команд
        
        Returns:
            int: Количество команд
        """
        try:
            return self.session.query(func.count(Team.id)).scalar()
        except Exception as e:
            print(f"Ошибка при подсчете команд: {str(e)}")
            return 0
    
    def get_team_players(self, team_id):
        """
        Получение списка игроков команды
        
        Args:
            team_id (int): ID команды
            
        Returns:
            list: Список игроков команды
        """
        try:
            return self.session.query(Player).filter(
                Player.team_id == team_id,
                Player.is_active == True
            ).order_by(Player.last_name, Player.first_name).all()
        except Exception as e:
            print(f"Ошибка при получении игроков команды: {str(e)}")
            return []
    
    def get_all_tournaments(self):
        """
        Получение списка всех турниров
        
        Returns:
            list: Список турниров
        """
        try:
            return self.session.query(Tournament).order_by(Tournament.start_date.desc()).all()
        except Exception as e:
            print(f"Ошибка при получении списка турниров: {str(e)}")
            return []
    
    def get_tournament_by_id(self, tournament_id):
        """
        Получение турнира по ID
        
        Args:
            tournament_id (int): ID турнира
            
        Returns:
            Tournament: Объект турнира или None, если турнир не найден
        """
        try:
            return self.session.query(Tournament).filter(Tournament.id == tournament_id).first()
        except Exception as e:
            print(f"Ошибка при получении турнира: {str(e)}")
            return None
    
    def create_tournament(self, tournament_data):
        """
        Создание нового турнира
        
        Args:
            tournament_data (dict): Данные турнира
            
        Returns:
            Tournament: Созданный турнир или None в случае ошибки
        """
        try:
            # Создание нового турнира
            tournament = Tournament(
                name=tournament_data.get('name'),
                start_date=tournament_data.get('start_date'),
                end_date=tournament_data.get('end_date'),
                location=tournament_data.get('location'),
                description=tournament_data.get('description')
            )
            
            # Сохранение турнира
            self.session.add(tournament)
            self.session.commit()
            
            return tournament
        except Exception as e:
            print(f"Ошибка при создании турнира: {str(e)}")
            self.session.rollback()
            return None
    
    def update_tournament(self, tournament_id, tournament_data):
        """
        Обновление данных турнира
        
        Args:
            tournament_id (int): ID турнира
            tournament_data (dict): Новые данные турнира
            
        Returns:
            Tournament: Обновленный турнир или None в случае ошибки
        """
        try:
            # Поиск турнира
            tournament = self.session.query(Tournament).filter(Tournament.id == tournament_id).first()
            
            if not tournament:
                return None
            
            # Обновление данных
            tournament.name = tournament_data.get('name', tournament.name)
            tournament.start_date = tournament_data.get('start_date', tournament.start_date)
            tournament.end_date = tournament_data.get('end_date', tournament.end_date)
            tournament.location = tournament_data.get('location', tournament.location)
            tournament.description = tournament_data.get('description', tournament.description)
            
            self.session.commit()
            
            return tournament
        except Exception as e:
            print(f"Ошибка при обновлении турнира: {str(e)}")
            self.session.rollback()
            return None
    
    def delete_tournament(self, tournament_id):
        """
        Удаление турнира
        
        Args:
            tournament_id (int): ID турнира
            
        Returns:
            bool: True при успешном удалении, False в противном случае
        """
        try:
            # Поиск турнира
            tournament = self.session.query(Tournament).filter(Tournament.id == tournament_id).first()
            
            if not tournament:
                return False
            
            # Удаление турнира
            self.session.delete(tournament)
            self.session.commit()
            
            return True
        except Exception as e:
            print(f"Ошибка при удалении турнира: {str(e)}")
            self.session.rollback()
            return False
    
    def get_tournament_teams(self, tournament_id):
        """
        Получение списка команд, участвующих в турнире
        
        Args:
            tournament_id (int): ID турнира
            
        Returns:
            list: Список команд-участников
        """
        try:
            return self.session.query(TournamentTeam).filter(
                TournamentTeam.tournament_id == tournament_id
            ).order_by(TournamentTeam.rank).all()
        except Exception as e:
            print(f"Ошибка при получении команд турнира: {str(e)}")
            return []
    
    def get_available_teams_for_tournament(self, tournament_id):
        """
        Получение списка команд, которые можно добавить в турнир
        
        Args:
            tournament_id (int): ID турнира
            
        Returns:
            list: Список доступных команд
        """
        try:
            # Получение ID команд, уже участвующих в турнире
            subquery = self.session.query(TournamentTeam.team_id).filter(
                TournamentTeam.tournament_id == tournament_id
            ).subquery()
            
            # Получение команд, которые не участвуют в турнире
            teams = self.session.query(Team).filter(
                ~Team.id.in_(subquery)
            ).order_by(Team.name).all()
            
            return teams
        except Exception as e:
            print(f"Ошибка при получении доступных команд: {str(e)}")
            return []
    
    def add_team_to_tournament(self, data):
        """
        Добавление команды в турнир
        
        Args:
            data (dict): Данные связи команды и турнира
            
        Returns:
            TournamentTeam: Созданная связь или None в случае ошибки
        """
        try:
            # Проверка наличия обязательных данных
            if 'tournament_id' not in data or 'team_id' not in data:
                return None
            
            # Создание связи
            tournament_team = TournamentTeam(
                tournament_id=data.get('tournament_id'),
                team_id=data.get('team_id'),
                rank=data.get('rank')
            )
            
            # Сохранение связи
            self.session.add(tournament_team)
            self.session.commit()
            
            return tournament_team
        except Exception as e:
            print(f"Ошибка при добавлении команды в турнир: {str(e)}")
            self.session.rollback()
            return None
    
    def remove_team_from_tournament(self, tournament_team_id):
        """
        Удаление команды из турнира
        
        Args:
            tournament_team_id (int): ID связи команды и турнира
            
        Returns:
            bool: True при успешном удалении, False в противном случае
        """
        try:
            # Поиск связи
            tournament_team = self.session.query(TournamentTeam).filter(
                TournamentTeam.id == tournament_team_id
            ).first()
            
            if not tournament_team:
                return False
            
            # Удаление связи
            self.session.delete(tournament_team)
            self.session.commit()
            
            return True
        except Exception as e:
            print(f"Ошибка при удалении команды из турнира: {str(e)}")
            self.session.rollback()
            return False
    
    def update_team_rank(self, tournament_team_id, rank):
        """
        Обновление места команды в турнире
        
        Args:
            tournament_team_id (int): ID связи команды и турнира
            rank (int): Новое место в турнире
            
        Returns:
            bool: True при успешном обновлении, False в противном случае
        """
        try:
            # Поиск связи
            tournament_team = self.session.query(TournamentTeam).filter(
                TournamentTeam.id == tournament_team_id
            ).first()
            
            if not tournament_team:
                return False
            
            # Обновление места
            tournament_team.rank = rank
            self.session.commit()
            
            return True
        except Exception as e:
            print(f"Ошибка при обновлении места команды: {str(e)}")
            self.session.rollback()
            return False

