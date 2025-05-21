#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Консольная версия приложения "Рабочее место тренера хоккейной команды"
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

def clear_screen():
    """Очистка консоли"""
    if os.name == 'nt':  # для Windows
        os.system('cls')
    else:  # для Linux/Mac
        os.system('clear')

def print_header(title):
    """Печать заголовка"""
    clear_screen()
    print("=" * 80)
    print(f"{title}".center(80))
    print("=" * 80)
    print()

def print_menu(options):
    """Печать меню"""
    for key, value in options.items():
        print(f"{key}. {value}")
    print()

def get_menu_choice(options):
    """Получение выбора пользователя из меню"""
    while True:
        choice = input("Выберите пункт меню: ")
        if choice in options:
            return choice
        print("Некорректный выбор. Повторите попытку.")

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

def auth_menu():
    """Меню авторизации"""
    print_header("Авторизация")
    
    print("Для входа в систему введите имя пользователя и пароль.")
    print("По умолчанию: имя пользователя - 'admin', пароль - 'admin'")
    print()
    
    auth_service = AuthService()
    
    attempts = 3
    while attempts > 0:
        username = input("Имя пользователя: ")
        password = input("Пароль: ")
        
        user = auth_service.authenticate(username, password)
        
        if user:
            print("\nАвторизация успешна!")
            time.sleep(1)
            return user
        else:
            attempts -= 1
            print(f"\nНеверное имя пользователя или пароль. Осталось попыток: {attempts}")
    
    print("\nСлишком много неудачных попыток. Выход из программы.")
    sys.exit(1)

def main_menu(user):
    """Основное меню приложения"""
    options = {
        '1': 'Команды',
        '2': 'Игроки',
        '3': 'Тренировки',
        '4': 'Матчи',
        '5': 'Статистика',
        '0': 'Выйти из программы'
    }
    
    while True:
        print_header(f"Главное меню - {user.full_name}")
        print_menu(options)
        
        choice = get_menu_choice(options)
        
        if choice == '1':
            teams_menu()
        elif choice == '2':
            players_menu()
        elif choice == '3':
            trainings_menu()
        elif choice == '4':
            matches_menu()
        elif choice == '5':
            stats_menu()
        elif choice == '0':
            print("\nВыход из программы...")
            sys.exit(0)

def teams_menu():
    """Меню команд"""
    options = {
        '1': 'Список команд',
        '2': 'Информация о команде',
        '0': 'Вернуться в главное меню'
    }
    
    team_service = TeamService()
    
    while True:
        print_header("Меню команд")
        print_menu(options)
        
        choice = get_menu_choice(options)
        
        if choice == '1':
            print_header("Список команд")
            
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
            
            input("Нажмите Enter для продолжения...")
        
        elif choice == '2':
            print_header("Информация о команде")
            
            team_id = input("Введите ID команды (0 для отмены): ")
            if team_id == '0':
                continue
            
            try:
                team_id = int(team_id)
                team = team_service.get_team_by_id(team_id)
                
                if team:
                    print(f"Название: {team.name}")
                    print(f"Домашняя арена: {team.home_arena or 'Не указана'}")
                    print(f"Год основания: {team.foundation_year or 'Не указан'}")
                    
                    # Тренер
                    coach_name = team.coach.full_name if team.coach else "Не назначен"
                    print(f"Тренер: {coach_name}")
                    
                    # Игроки команды
                    players = team_service.get_team_players(team_id)
                    
                    print("\nСостав команды:")
                    if not players:
                        print("Игроки не найдены.")
                    else:
                        headers = ["ID", "Имя", "Фамилия", "Позиция", "Номер"]
                        data = []
                        
                        for player in players:
                            data.append([
                                player.id,
                                player.first_name,
                                player.last_name,
                                player.position,
                                player.jersey_number or "-"
                            ])
                        
                        print_data_table(headers, data)
                else:
                    print("Команда не найдена.")
            except ValueError:
                print("Некорректный ID. Введите число.")
            
            input("Нажмите Enter для продолжения...")
        
        elif choice == '0':
            break

def players_menu():
    """Меню игроков"""
    options = {
        '1': 'Список игроков',
        '2': 'Информация об игроке',
        '3': 'Поиск игрока',
        '0': 'Вернуться в главное меню'
    }
    
    player_service = PlayerService()
    
    while True:
        print_header("Меню игроков")
        print_menu(options)
        
        choice = get_menu_choice(options)
        
        if choice == '1':
            print_header("Список игроков")
            
            team_id = input("Введите ID команды (0 для всех команд): ")
            team_id = int(team_id) if team_id != '0' else None
            
            players = player_service.get_players(team_id=team_id)
            
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
            
            input("Нажмите Enter для продолжения...")
        
        elif choice == '2':
            print_header("Информация об игроке")
            
            player_id = input("Введите ID игрока (0 для отмены): ")
            if player_id == '0':
                continue
            
            try:
                player_id = int(player_id)
                player = player_service.get_player_by_id(player_id)
                
                if player:
                    print(f"Имя: {player.first_name}")
                    print(f"Фамилия: {player.last_name}")
                    print(f"Отчество: {player.middle_name or 'Не указано'}")
                    print(f"Позиция: {player.position}")
                    print(f"Номер: {player.jersey_number or 'Не указан'}")
                    
                    if player.birth_date:
                        age = (date.today() - player.birth_date).days // 365
                        print(f"Дата рождения: {player.birth_date} ({age} лет)")
                    else:
                        print("Дата рождения: Не указана")
                    
                    print(f"Рост: {player.height or 'Не указан'} см")
                    print(f"Вес: {player.weight or 'Не указан'} кг")
                    print(f"Команда: {player.team.name if player.team else 'Не назначена'}")
                    
                    if player.notes:
                        print(f"\nПримечания: {player.notes}")
                else:
                    print("Игрок не найден.")
            except ValueError:
                print("Некорректный ID. Введите число.")
            
            input("Нажмите Enter для продолжения...")
        
        elif choice == '3':
            print_header("Поиск игрока")
            
            search_term = input("Введите имя или фамилию игрока: ")
            
            if search_term:
                players = player_service.search_players(search_term)
                
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
            else:
                print("Введите поисковый запрос.")
            
            input("Нажмите Enter для продолжения...")
        
        elif choice == '0':
            break

def trainings_menu():
    """Меню тренировок"""
    options = {
        '1': 'Список тренировок',
        '2': 'Информация о тренировке',
        '3': 'Предстоящие тренировки',
        '0': 'Вернуться в главное меню'
    }
    
    training_service = TrainingService()
    
    while True:
        print_header("Меню тренировок")
        print_menu(options)
        
        choice = get_menu_choice(options)
        
        if choice == '1':
            print_header("Список тренировок")
            
            team_id = input("Введите ID команды (0 для всех команд): ")
            team_id = int(team_id) if team_id != '0' else None
            
            trainings = training_service.get_trainings(team_id=team_id)
            
            if not trainings:
                print("Тренировки не найдены.")
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
            
            input("Нажмите Enter для продолжения...")
        
        elif choice == '2':
            print_header("Информация о тренировке")
            
            training_id = input("Введите ID тренировки (0 для отмены): ")
            if training_id == '0':
                continue
            
            try:
                training_id = int(training_id)
                training = training_service.get_training_by_id(training_id)
                
                if training:
                    team_name = training.team.name if training.team else "Не указана"
                    
                    print(f"Дата: {training.date}")
                    print(f"Время: {training.start_time} - {training.end_time}")
                    print(f"Команда: {team_name}")
                    print(f"Место: {training.location or 'Не указано'}")
                    print(f"Направление: {training.focus_area or 'Общая тренировка'}")
                    
                    if training.description:
                        print(f"\nОписание: {training.description}")
                    
                    # Упражнения тренировки
                    exercises = training_service.get_training_exercises(training_id)
                    
                    print("\nПлан тренировки:")
                    if not exercises:
                        print("Упражнения не добавлены.")
                    else:
                        headers = ["#", "Название", "Длительность (мин)", "Описание"]
                        data = []
                        
                        for exercise in exercises:
                            data.append([
                                exercise.order,
                                exercise.name,
                                exercise.duration or "-",
                                (exercise.description[:30] + "...") if exercise.description and len(exercise.description) > 30 else (exercise.description or "-")
                            ])
                        
                        print_data_table(headers, data)
                    
                    # Посещаемость
                    attendance = training_service.get_training_attendance(training_id)
                    
                    print("\nПосещаемость:")
                    if not attendance:
                        print("Данные о посещаемости отсутствуют.")
                    else:
                        headers = ["Игрок", "Присутствие", "Причина отсутствия"]
                        data = []
                        
                        for record in attendance:
                            player_name = f"{record.player.last_name} {record.player.first_name}" if record.player else "Неизвестный игрок"
                            data.append([
                                player_name,
                                "Да" if record.is_present else "Нет",
                                record.reason or "-" if not record.is_present else "-"
                            ])
                        
                        print_data_table(headers, data)
                else:
                    print("Тренировка не найдена.")
            except ValueError:
                print("Некорректный ID. Введите число.")
            
            input("Нажмите Enter для продолжения...")
        
        elif choice == '3':
            print_header("Предстоящие тренировки")
            
            days = input("Введите количество дней для просмотра (по умолчанию 7): ")
            days = int(days) if days and days.isdigit() else 7
            
            trainings = training_service.get_upcoming_trainings(days=days)
            
            if not trainings:
                print(f"Предстоящие тренировки на ближайшие {days} дней не найдены.")
            else:
                headers = ["ID", "Дата", "Время", "Команда", "Место"]
                data = []
                
                for training in trainings:
                    team_name = training.team.name if training.team else "Не указана"
                    data.append([
                        training.id,
                        training.date,
                        f"{training.start_time} - {training.end_time}",
                        team_name,
                        training.location or "Не указано"
                    ])
                
                print_data_table(headers, data)
            
            input("Нажмите Enter для продолжения...")
        
        elif choice == '0':
            break

def matches_menu():
    """Меню матчей"""
    options = {
        '1': 'Список матчей',
        '2': 'Информация о матче',
        '3': 'Предстоящие матчи',
        '4': 'Прошедшие матчи',
        '0': 'Вернуться в главное меню'
    }
    
    match_service = MatchService()
    
    while True:
        print_header("Меню матчей")
        print_menu(options)
        
        choice = get_menu_choice(options)
        
        if choice == '1':
            print_header("Список матчей")
            
            team_id = input("Введите ID команды (0 для всех команд): ")
            team_id = int(team_id) if team_id != '0' else None
            
            matches = match_service.get_matches(team_id=team_id)
            
            if not matches:
                print("Матчи не найдены.")
            else:
                headers = ["ID", "Дата", "Время", "Домашняя команда", "Гостевая команда", "Счет", "Статус"]
                data = []
                
                for match in matches:
                    home_team = match.home_team.name if match.home_team else "Неизвестно"
                    away_team = match.away_team.name if match.away_team else "Неизвестно"
                    
                    score = f"{match.home_score}:{match.away_score}" if match.home_score is not None and match.away_score is not None else "-"
                    
                    data.append([
                        match.id,
                        match.date,
                        match.time or "-",
                        home_team,
                        away_team,
                        score,
                        match.status
                    ])
                
                print_data_table(headers, data)
            
            input("Нажмите Enter для продолжения...")
        
        elif choice == '2':
            print_header("Информация о матче")
            
            match_id = input("Введите ID матча (0 для отмены): ")
            if match_id == '0':
                continue
            
            try:
                match_id = int(match_id)
                match = match_service.get_match_by_id(match_id)
                
                if match:
                    home_team = match.home_team.name if match.home_team else "Неизвестно"
                    away_team = match.away_team.name if match.away_team else "Неизвестно"
                    
                    print(f"Дата: {match.date}")
                    print(f"Время: {match.time or 'Не указано'}")
                    print(f"Место: {match.location or 'Не указано'}")
                    print(f"Домашняя команда: {home_team}")
                    print(f"Гостевая команда: {away_team}")
                    
                    if match.home_score is not None and match.away_score is not None:
                        print(f"Счет: {match.home_score}:{match.away_score}")
                    
                    print(f"Статус: {match.status}")
                    
                    if match.notes:
                        print(f"\nПримечания: {match.notes}")
                    
                    if match.video_path:
                        print(f"\nВидеозапись: {match.video_path}")
                    
                    # Получение видео матча
                    videos = match_service.get_match_videos(match_id)
                    
                    if videos:
                        print("\nВидеоматериалы:")
                        for i, video in enumerate(videos, 1):
                            print(f"{i}. {video['title']} ({video['uploaded_at']})")
                    
                else:
                    print("Матч не найден.")
            except ValueError:
                print("Некорректный ID. Введите число.")
            
            input("Нажмите Enter для продолжения...")
        
        elif choice == '3':
            print_header("Предстоящие матчи")
            
            days = input("Введите количество дней для просмотра (по умолчанию 7): ")
            days = int(days) if days and days.isdigit() else 7
            
            matches = match_service.get_upcoming_matches(days=days)
            
            if not matches:
                print(f"Предстоящие матчи на ближайшие {days} дней не найдены.")
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
            
            input("Нажмите Enter для продолжения...")
        
        elif choice == '4':
            print_header("Прошедшие матчи")
            
            days = input("Введите количество дней для просмотра (по умолчанию 7): ")
            days = int(days) if days and days.isdigit() else 7
            
            matches = match_service.get_past_matches(days=days)
            
            if not matches:
                print(f"Прошедшие матчи за последние {days} дней не найдены.")
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
            
            input("Нажмите Enter для продолжения...")
        
        elif choice == '0':
            break

def stats_menu():
    """Меню статистики"""
    options = {
        '1': 'Статистика игрока',
        '2': 'Статистика команды',
        '3': 'Лучшие игроки',
        '0': 'Вернуться в главное меню'
    }
    
    stats_service = StatsService()
    
    while True:
        print_header("Меню статистики")
        print_menu(options)
        
        choice = get_menu_choice(options)
        
        if choice == '1':
            print_header("Статистика игрока")
            
            player_id = input("Введите ID игрока (0 для отмены): ")
            if player_id == '0':
                continue
            
            try:
                player_id = int(player_id)
                
                # Получение игрока и его статистики
                player_service = PlayerService()
                player = player_service.get_player_by_id(player_id)
                
                if player:
                    print(f"Игрок: {player.last_name} {player.first_name}")
                    print(f"Позиция: {player.position}")
                    print(f"Команда: {player.team.name if player.team else 'Не назначена'}")
                    print()
                    
                    # Получение статистики
                    stats = stats_service.get_player_stats(player_id)
                    
                    print("Статистика:")
                    print(f"Матчи: {stats['games']}")
                    print(f"Голы: {stats['goals']}")
                    print(f"Передачи: {stats['assists']}")
                    print(f"Очки (гол+пас): {stats['points']}")
                    print(f"Штрафные минуты: {stats['penalty_minutes']}")
                    print(f"Плюс/минус: {stats['plus_minus']}")
                    print(f"Броски: {stats['shots']}")
                    
                    # Расчет процента реализации, если есть броски
                    if stats['shots'] > 0:
                        shooting_pct = (stats['goals'] / stats['shots']) * 100
                        print(f"Процент реализации: {shooting_pct:.2f}%")
                    
                    # Время на льду
                    if stats['time_on_ice'] > 0:
                        avg_time = stats['time_on_ice'] / stats['games'] if stats['games'] > 0 else 0
                        print(f"Среднее время на льду: {avg_time // 60:02d}:{avg_time % 60:02d}")
                    
                    # Вбрасывания
                    if stats['faceoffs_total'] > 0:
                        print(f"Вбрасывания: {stats['faceoffs_won']} из {stats['faceoffs_total']} ({stats['faceoff_percentage']:.2f}%)")
                    
                else:
                    print("Игрок не найден.")
            except ValueError:
                print("Некорректный ID. Введите число.")
            
            input("Нажмите Enter для продолжения...")
        
        elif choice == '2':
            print_header("Статистика команды")
            
            team_id = input("Введите ID команды (0 для отмены): ")
            if team_id == '0':
                continue
            
            try:
                team_id = int(team_id)
                
                # Получение команды и её статистики
                team_service = TeamService()
                team = team_service.get_team_by_id(team_id)
                
                if team:
                    print(f"Команда: {team.name}")
                    print()
                    
                    # Получение статистики
                    stats = stats_service.get_team_stats(team_id)
                    
                    print("Общая статистика:")
                    print(f"Матчи: {stats['games']}")
                    print(f"Победы: {stats['wins']}")
                    print(f"Поражения: {stats['losses']}")
                    print(f"Процент побед: {stats['win_percentage']:.2f}%")
                    print()
                    
                    print("Атака:")
                    print(f"Забитые голы: {stats['goals_for']}")
                    print(f"Среднее за игру: {stats['goals_for'] / stats['games']:.2f}" if stats['games'] > 0 else "Среднее за игру: 0.00")
                    print()
                    
                    print("Защита:")
                    print(f"Пропущенные голы: {stats['goals_against']}")
                    print(f"Среднее за игру: {stats['goals_against'] / stats['games']:.2f}" if stats['games'] > 0 else "Среднее за игру: 0.00")
                    print()
                    
                    print("Большинство:")
                    print(f"Голы в большинстве: {stats['powerplay_goals']}")
                    print(f"Реализация большинства: {stats['powerplay_percentage']:.2f}%")
                    print()
                    
                    print("Другое:")
                    print(f"Штрафные минуты: {stats['penalty_minutes']}")
                    print(f"Голы в меньшинстве: {stats['shorthanded_goals_for']}")
                    print(f"Броски: {stats['shots_for']} (за), {stats['shots_against']} (против)")
                    
                else:
                    print("Команда не найдена.")
            except ValueError:
                print("Некорректный ID. Введите число.")
            
            input("Нажмите Enter для продолжения...")
        
        elif choice == '3':
            print_header("Лучшие игроки")
            
            print("Выберите категорию:")
            categories = {
                '1': 'Очки (гол+пас)',
                '2': 'Голы',
                '3': 'Передачи',
                '4': 'Плюс/минус',
                '0': 'Отмена'
            }
            
            print_menu(categories)
            category_choice = get_menu_choice(categories)
            
            if category_choice == '0':
                continue
            
            category_map = {
                '1': 'points',
                '2': 'goals',
                '3': 'assists',
                '4': 'plus_minus'
            }
            
            category = category_map.get(category_choice)
            
            team_id = input("Введите ID команды (0 для всех команд): ")
            team_id = int(team_id) if team_id != '0' else None
            
            limit = input("Введите количество игроков для отображения (по умолчанию 10): ")
            limit = int(limit) if limit and limit.isdigit() else 10
            
            players = stats_service.get_top_players(team_id=team_id, category=category, limit=limit)
            
            if not players:
                print("Нет данных для отображения.")
            else:
                headers = ["#", "Игрок", "Команда", "Позиция", "Значение"]
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
            
            input("Нажмите Enter для продолжения...")
        
        elif choice == '0':
            break

def main():
    """Основная функция"""
    try:
        # Инициализация базы данных
        init_db()
        
        # Авторизация
        user = auth_menu()
        
        # Основное меню
        main_menu(user)
    except KeyboardInterrupt:
        print("\nВыход из программы...")
        sys.exit(0)
    except Exception as e:
        print(f"\nПроизошла ошибка: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()