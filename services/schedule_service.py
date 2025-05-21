# -*- coding: utf-8 -*-

"""
Сервис для работы с расписаниями матчей и тренировок
"""

from datetime import date, timedelta, datetime
from sqlalchemy import and_, or_, func

from database import get_session
from models import Match, Training, Team

class ScheduleService:
    """Сервис для работы с расписаниями"""
    
    def __init__(self):
        """Инициализация сервиса"""
        self.session = get_session()
    
    def get_schedule(self, team_id=None, start_date=None, end_date=None, include_matches=True, include_trainings=True):
        """
        Получение расписания (матчи и тренировки)
        
        Args:
            team_id (int, optional): ID команды для фильтрации. Defaults to None.
            start_date (date, optional): Начальная дата. Defaults to None.
            end_date (date, optional): Конечная дата. Defaults to None.
            include_matches (bool, optional): Включать матчи. Defaults to True.
            include_trainings (bool, optional): Включать тренировки. Defaults to True.
            
        Returns:
            list: Список событий в расписании
        """
        try:
            schedule = []
            
            # Если начальная дата не указана, используем текущую
            if not start_date:
                start_date = date.today()
            
            # Если конечная дата не указана, используем дату через 30 дней
            if not end_date:
                end_date = start_date + timedelta(days=30)
            
            # Получение матчей
            if include_matches:
                matches_query = self.session.query(Match).filter(Match.date.between(start_date, end_date))
                
                if team_id:
                    matches_query = matches_query.filter(
                        or_(
                            Match.home_team_id == team_id,
                            Match.away_team_id == team_id
                        )
                    )
                
                matches = matches_query.all()
                
                for match in matches:
                    # Получение названий команд
                    home_team = self.session.query(Team).get(match.home_team_id)
                    away_team = self.session.query(Team).get(match.away_team_id)
                    
                    home_team_name = home_team.name if home_team else "Неизвестная команда"
                    away_team_name = away_team.name if away_team else "Неизвестная команда"
                    
                    # Добавление матча в расписание
                    schedule.append({
                        'id': match.id,
                        'type': 'match',
                        'date': match.date,
                        'time': match.time,
                        'title': f"{home_team_name} vs {away_team_name}",
                        'location': match.location,
                        'status': match.status,
                        'details': {
                            'home_team_id': match.home_team_id,
                            'away_team_id': match.away_team_id,
                            'home_team_name': home_team_name,
                            'away_team_name': away_team_name,
                            'home_score': match.home_score,
                            'away_score': match.away_score
                        }
                    })
            
            # Получение тренировок
            if include_trainings:
                trainings_query = self.session.query(Training).filter(Training.date.between(start_date, end_date))
                
                if team_id:
                    trainings_query = trainings_query.filter(Training.team_id == team_id)
                
                trainings = trainings_query.all()
                
                for training in trainings:
                    # Получение названия команды
                    team = self.session.query(Team).get(training.team_id)
                    team_name = team.name if team else "Неизвестная команда"
                    
                    # Добавление тренировки в расписание
                    schedule.append({
                        'id': training.id,
                        'type': 'training',
                        'date': training.date,
                        'time': training.start_time,
                        'title': f"Тренировка ({team_name})",
                        'location': training.location,
                        'status': 'активна',
                        'details': {
                            'team_id': training.team_id,
                            'team_name': team_name,
                            'end_time': training.end_time,
                            'focus_area': training.focus_area,
                            'description': training.description
                        }
                    })
            
            # Сортировка расписания по дате и времени
            schedule.sort(key=lambda x: (x['date'], x['time']))
            
            return schedule
        except Exception as e:
            print(f"Ошибка при получении расписания: {str(e)}")
            return []
    
    def get_weekly_schedule(self, team_id=None, week_start=None):
        """
        Получение расписания на неделю
        
        Args:
            team_id (int, optional): ID команды для фильтрации. Defaults to None.
            week_start (date, optional): Начало недели. Defaults to None.
            
        Returns:
            dict: Расписание на неделю по дням
        """
        try:
            # Если начало недели не указано, используем текущую дату
            if not week_start:
                today = date.today()
                # Получаем понедельник текущей недели
                week_start = today - timedelta(days=today.weekday())
            
            # Конец недели - воскресенье
            week_end = week_start + timedelta(days=6)
            
            # Получаем общее расписание на неделю
            events = self.get_schedule(team_id, week_start, week_end)
            
            # Группируем события по дням недели
            weekly_schedule = {
                'week_start': week_start,
                'week_end': week_end,
                'days': {}
            }
            
            # Инициализация словаря с днями недели
            for i in range(7):
                day = week_start + timedelta(days=i)
                day_name = self._get_day_name(day)
                weekly_schedule['days'][day_name] = {
                    'date': day,
                    'events': []
                }
            
            # Распределение событий по дням
            for event in events:
                event_date = event['date']
                day_name = self._get_day_name(event_date)
                weekly_schedule['days'][day_name]['events'].append(event)
            
            return weekly_schedule
        except Exception as e:
            print(f"Ошибка при получении недельного расписания: {str(e)}")
            return {}
    
    def _get_day_name(self, date_obj):
        """
        Получение названия дня недели
        
        Args:
            date_obj (date): Дата
            
        Returns:
            str: Название дня недели
        """
        days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
        return days[date_obj.weekday()]
    
    def get_next_events(self, team_id=None, days=7, limit=5):
        """
        Получение ближайших событий
        
        Args:
            team_id (int, optional): ID команды для фильтрации. Defaults to None.
            days (int, optional): Количество дней вперед. Defaults to 7.
            limit (int, optional): Лимит результатов. Defaults to 5.
            
        Returns:
            list: Список ближайших событий
        """
        try:
            today = date.today()
            end_date = today + timedelta(days=days)
            
            # Получаем расписание на указанный период
            events = self.get_schedule(team_id, today, end_date)
            
            # Ограничиваем количество результатов
            return events[:limit] if limit else events
        except Exception as e:
            print(f"Ошибка при получении ближайших событий: {str(e)}")
            return []
    
    def get_monthly_summary(self, team_id=None, month=None, year=None):
        """
        Получение сводки на месяц
        
        Args:
            team_id (int, optional): ID команды для фильтрации. Defaults to None.
            month (int, optional): Месяц (1-12). Defaults to None (текущий месяц).
            year (int, optional): Год. Defaults to None (текущий год).
            
        Returns:
            dict: Сводка на месяц
        """
        try:
            # Если месяц не указан, используем текущий
            if not month or not year:
                current_date = date.today()
                month = month or current_date.month
                year = year or current_date.year
            
            # Определяем начало и конец месяца
            start_date = date(year, month, 1)
            
            # Определяем последний день месяца
            if month == 12:
                end_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)
            
            # Получаем расписание на месяц
            events = self.get_schedule(team_id, start_date, end_date)
            
            # Подсчет статистики
            matches_count = sum(1 for event in events if event['type'] == 'match')
            trainings_count = sum(1 for event in events if event['type'] == 'training')
            
            # Группировка по дням
            days_with_events = {}
            for event in events:
                day = event['date'].day
                if day not in days_with_events:
                    days_with_events[day] = []
                days_with_events[day].append(event)
            
            return {
                'month': month,
                'year': year,
                'start_date': start_date,
                'end_date': end_date,
                'total_events': len(events),
                'matches_count': matches_count,
                'trainings_count': trainings_count,
                'days_with_events': days_with_events
            }
        except Exception as e:
            print(f"Ошибка при получении сводки на месяц: {str(e)}")
            return {}