#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Упрощенная версия приложения "Рабочее место тренера хоккейной команды"
для запуска в среде Replit без ввода пользователя
"""

import sys
import os
import time
from datetime import date, datetime, timedelta

from database import init_db, get_session
from models import User, Team, Player, Training, Match
from services.auth_service import AuthService
from services.player_service import PlayerService
from services.team_service import TeamService
from services.training_service import TrainingService
from services.match_service import MatchService
from services.stats_service import StatsService
from config import Config

def print_header(title):
    """Печать заголовка"""
    print("=" * 80)
    print(f"{title}".center(80))
    print("=" * 80)
    print()

def print_data_table(headers, data):
    """Печать таблицы данных"""
    # Определение ширины колонок
    col_widths = []
    for i, header in enumerate(headers):
        max_width = len(header)
        for row in data:
            if i < len(row) and row[i] is not None:
                max_width = max(max_width, len(str(row[i])))
        col_widths.append(max_width + 2)
    
    # Печать заголовков
    header_line = ""
    for i, header in enumerate(headers):
        header_line += header.ljust(col_widths[i])
    print(header_line)
    
    # Печать разделителя
    print("-" * sum(col_widths))
    
    # Печать данных
    for row in data:
        line = ""
        for i, value in enumerate(row):
            if i < len(col_widths):
                if value is None:
                    value = ""
                line += str(value).ljust(col_widths[i])
        print(line)
    print()

def demo_data():
    """Вставка демонстрационных данных в базу"""
    print("Проверка наличия демонстрационных данных...")
    
    session = get_session()
    
    # Проверка наличия команд
    teams_count = session.query(Team).count()
    if teams_count > 0:
        print(f"В базе данных уже есть {teams_count} команд.")
        session.close()
        return
    
    print("Добавление демонстрационных данных...")
    
    # Создание пользователя-администратора, если он не существует
    auth_service = AuthService()
    admin = session.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(
            username="admin",
            full_name="Администратор",
            is_admin=True
        )
        admin.set_password("admin")
        session.add(admin)
        session.commit()
        print("Создан пользователь администратор (admin/admin)")
    
    # Создание команд
    team1 = Team(
        name="Спартак",
        home_arena="СК Спартак",
        foundation_year=1985,
        coach_id=admin.id,
        description="Хоккейный клуб Спартак",
        is_opponent=False
    )
    
    team2 = Team(
        name="ЦСКА",
        home_arena="ЛДС ЦСКА",
        foundation_year=1983,
        description="Хоккейный клуб ЦСКА",
        is_opponent=True
    )
    
    team3 = Team(
        name="Динамо",
        home_arena="ВТБ Арена",
        foundation_year=1980,
        description="Хоккейный клуб Динамо",
        is_opponent=True
    )
    
    session.add_all([team1, team2, team3])
    session.commit()
    print(f"Созданы команды: {team1.name}, {team2.name}, {team3.name}")
    
    # Создание игроков для команды Спартак
    positions = ["нападающий", "защитник", "вратарь"]
    
    players = [
        Player(
            first_name="Иван",
            last_name="Петров",
            middle_name="Сергеевич",
            birth_date=date(1992, 7, 15),
            position=positions[0],  # нападающий
            jersey_number=10,
            height=180,
            weight=85,
            team_id=team1.id,
            is_active=True
        ),
        Player(
            first_name="Алексей",
            last_name="Смирнов",
            middle_name="Иванович",
            birth_date=date(1994, 5, 22),
            position=positions[0],  # нападающий
            jersey_number=19,
            height=178,
            weight=82,
            team_id=team1.id,
            is_active=True
        ),
        Player(
            first_name="Сергей",
            last_name="Иванов",
            middle_name="Петрович",
            birth_date=date(1991, 11, 30),
            position=positions[1],  # защитник
            jersey_number=55,
            height=185,
            weight=90,
            team_id=team1.id,
            is_active=True
        ),
        Player(
            first_name="Михаил",
            last_name="Козлов",
            middle_name="Александрович",
            birth_date=date(1993, 3, 5),
            position=positions[1],  # защитник
            jersey_number=77,
            height=187,
            weight=93,
            team_id=team1.id,
            is_active=True
        ),
        Player(
            first_name="Дмитрий",
            last_name="Соколов",
            middle_name="Андреевич",
            birth_date=date(1990, 9, 12),
            position=positions[2],  # вратарь
            jersey_number=30,
            height=183,
            weight=87,
            team_id=team1.id,
            is_active=True
        )
    ]
    
    session.add_all(players)
    session.commit()
    print(f"Создано {len(players)} игроков для команды {team1.name}")
    
    # Создание тренировок
    today = date.today()
    
    trainings = [
        Training(
            date=today + timedelta(days=1),
            start_time=datetime.strptime("10:00", "%H:%M").time(),
            end_time=datetime.strptime("12:00", "%H:%M").time(),
            team_id=team1.id,
            location="СК Спартак",
            focus_area="Общая подготовка",
            description="Отработка командных взаимодействий"
        ),
        Training(
            date=today + timedelta(days=3),
            start_time=datetime.strptime("11:00", "%H:%M").time(),
            end_time=datetime.strptime("13:30", "%H:%M").time(),
            team_id=team1.id,
            location="СК Спартак",
            focus_area="Тактика",
            description="Тактические схемы в нападении"
        ),
        Training(
            date=today + timedelta(days=5),
            start_time=datetime.strptime("09:30", "%H:%M").time(),
            end_time=datetime.strptime("11:30", "%H:%M").time(),
            team_id=team1.id,
            location="СК Спартак",
            focus_area="Физическая подготовка",
            description="Силовые упражнения и развитие выносливости"
        )
    ]
    
    session.add_all(trainings)
    session.commit()
    print(f"Создано {len(trainings)} тренировок")
    
    # Создание матчей
    matches = [
        Match(
            date=today + timedelta(days=7),
            time=datetime.strptime("19:00", "%H:%M").time(),
            home_team_id=team1.id,
            away_team_id=team2.id,
            location="СК Спартак",
            status="запланирован"
        ),
        Match(
            date=today + timedelta(days=14),
            time=datetime.strptime("17:30", "%H:%M").time(),
            home_team_id=team3.id,
            away_team_id=team1.id,
            location="ВТБ Арена",
            status="запланирован"
        ),
        Match(
            date=today - timedelta(days=5),
            time=datetime.strptime("18:00", "%H:%M").time(),
            home_team_id=team1.id,
            away_team_id=team3.id,
            location="СК Спартак",
            status="завершен",
            home_score=3,
            away_score=2
        )
    ]
    
    session.add_all(matches)
    session.commit()
    print(f"Создано {len(matches)} матчей")
    
    session.close()
    print("Демонстрационные данные успешно добавлены!")

def show_team_list():
    """Показ списка команд"""
    print_header("Список команд")
    
    team_service = TeamService()
    teams = team_service.get_all_teams()
    
    if not teams:
        print("Команды не найдены.")
    else:
        headers = ["ID", "Название", "Арена", "Год основания", "Тренер"]
        data = []
        
        for team in teams:
            coach_name = team.coach.full_name if team.coach else "Не назначен"
            data.append([
                team.id,
                team.name,
                team.home_arena or "Не указана",
                team.foundation_year or "Не указан",
                coach_name
            ])
        
        print_data_table(headers, data)

def show_players_list():
    """Показ списка игроков"""
    print_header("Список игроков")
    
    player_service = PlayerService()
    players = player_service.get_players()
    
    if not players:
        print("Игроки не найдены.")
    else:
        headers = ["ID", "Имя", "Фамилия", "Позиция", "Номер", "Команда"]
        data = []
        
        for player in players:
            team_name = player.team.name if player.team else "Не назначена"
            data.append([
                player.id,
                player.first_name,
                player.last_name,
                player.position,
                player.jersey_number or "-",
                team_name
            ])
        
        print_data_table(headers, data)

def show_training_schedule():
    """Показ расписания тренировок"""
    print_header("Расписание тренировок")
    
    training_service = TrainingService()
    trainings = training_service.get_upcoming_trainings(days=14)
    
    if not trainings:
        print("Предстоящие тренировки не найдены.")
    else:
        headers = ["ID", "Дата", "Время", "Команда", "Место", "Направление"]
        data = []
        
        for training in trainings:
            team_name = training.team.name if training.team else "Не указана"
            data.append([
                training.id,
                training.date,
                f"{training.start_time} - {training.end_time}",
                team_name,
                training.location or "Не указано",
                training.focus_area or "Общая"
            ])
        
        print_data_table(headers, data)

def show_match_schedule():
    """Показ расписания матчей"""
    print_header("Расписание матчей")
    
    match_service = MatchService()
    matches = match_service.get_upcoming_matches(days=30)
    
    if not matches:
        print("Предстоящие матчи не найдены.")
    else:
        headers = ["ID", "Дата", "Время", "Домашняя команда", "Гостевая команда", "Место"]
        data = []
        
        for match in matches:
            home_team = match.home_team.name if match.home_team else "Неизвестно"
            away_team = match.away_team.name if match.away_team else "Неизвестно"
            
            data.append([
                match.id,
                match.date,
                match.time or "-",
                home_team,
                away_team,
                match.location or "Не указано"
            ])
        
        print_data_table(headers, data)

def show_past_matches():
    """Показ прошедших матчей"""
    print_header("Прошедшие матчи")
    
    match_service = MatchService()
    matches = match_service.get_past_matches(days=30)
    
    if not matches:
        print("Прошедшие матчи не найдены.")
    else:
        headers = ["ID", "Дата", "Домашняя команда", "Гостевая команда", "Счет"]
        data = []
        
        for match in matches:
            home_team = match.home_team.name if match.home_team else "Неизвестно"
            away_team = match.away_team.name if match.away_team else "Неизвестно"
            
            score = f"{match.home_score}:{match.away_score}" if match.home_score is not None and match.away_score is not None else "-"
            
            data.append([
                match.id,
                match.date,
                home_team,
                away_team,
                score
            ])
        
        print_data_table(headers, data)

def show_stats():
    """Показ статистики"""
    print_header("Лучшие игроки по очкам (гол+пас)")
    
    stats_service = StatsService()
    players = stats_service.get_top_players(category='points', limit=5)
    
    if not players:
        print("Нет данных для отображения.")
    else:
        headers = ["#", "Игрок", "Команда", "Позиция", "Очки"]
        data = []
        
        for i, player in enumerate(players, 1):
            data.append([
                i,
                f"{player['last_name']} {player['first_name']}",
                player['team_name'],
                player['position'],
                player['value']
            ])
        
        print_data_table(headers, data)

def main():
    """Основная функция приложения"""
    try:
        # Инициализация базы данных
        print("Инициализация базы данных...")
        init_db()
        
        # Добавление демонстрационных данных
        demo_data()
        
        # Авторизация без запроса учетных данных
        print_header("Авторизация")
        auth_service = AuthService()
        user = auth_service.authenticate("admin", "admin")
        
        if user:
            print(f"Успешный вход в систему как: {user.full_name}")
            print()
            
            # Демонстрация основных функций
            print_header("Демонстрация основных функций приложения")
            print("Приложение 'Рабочее место тренера хоккейной команды' предоставляет")
            print("следующие возможности для тренера:")
            print()
            print("1. Управление командами и составом")
            print("2. Планирование тренировок и матчей")
            print("3. Сбор и анализ статистики")
            print("4. Ведение учета посещаемости тренировок")
            print("5. Просмотр и анализ результатов матчей")
            print()
            
            # Демонстрация данных
            show_team_list()
            show_players_list()
            show_training_schedule()
            show_match_schedule()
            show_past_matches()
            show_stats()
            
            print_header("Завершение демонстрации")
            print("Это была демонстрация основных возможностей приложения")
            print("'Рабочее место тренера хоккейной команды'.")
            print()
            print("В полной версии доступны дополнительные функции:")
            print("- Полноценный графический интерфейс")
            print("- Добавление и редактирование всех данных")
            print("- Детальная статистика игроков и команд")
            print("- Работа с видеоматериалами")
            print("- Экспорт и печать отчетов")
            print()
        else:
            print("Ошибка авторизации!")
        
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()