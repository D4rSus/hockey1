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
        '6': 'Турниры',
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
        elif choice == '6':
            tournaments_menu()
        elif choice == '0':
            print("\nВыход из программы...")
            sys.exit(0)

def teams_menu():
    """Меню команд"""
    options = {
        '1': 'Список команд',
        '2': 'Информация о команде',
        '3': 'Добавить команду',
        '4': 'Редактировать команду',
        '5': 'Удалить команду',
        '6': 'Управление турнирами',
        '7': 'Экспорт списка команд в Excel',
        '0': 'Вернуться в главное меню'
    }
    
    team_service = TeamService()
    auth_service = AuthService()
    
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
        
        elif choice == '3':
            print_header("Добавление новой команды")
            print("Выберите тип создания:")
            creation_options = {
                '1': 'Быстрое создание (только название)',
                '2': 'Полное создание (все данные)',
                '0': 'Отмена'
            }
            print_menu(creation_options)
            creation_choice = get_menu_choice(creation_options)
            
            if creation_choice == '0':
                continue
                
            if creation_choice == '1':
                # Быстрое создание с указанием только названия
                name = input("Название команды: ")
                if not name:
                    print("Название команды обязательно для заполнения.")
                    input("Нажмите Enter для продолжения...")
                    continue
                
                # Создаем команду с минимальными данными
                team_data = {
                    'name': name,
                    'is_opponent': False  # По умолчанию не соперник
                }
                
                team = team_service.create_team(team_data)
                
                if team:
                    print(f"\nКоманда '{name}' успешно создана!")
                    
                    # Предложение добавить игроков в команду
                    add_players = input("\nХотите добавить игроков в команду? (да/нет): ").lower()
                    if add_players in ['да', 'д', 'yes', 'y', '1']:
                        add_players_to_team(team.id)
                else:
                    print("\nНе удалось создать команду. Проверьте введенные данные.")
                
                input("Нажмите Enter для продолжения...")
                continue
                
            # Полное создание команды
            name = input("Название команды: ")
            if not name:
                print("Название команды обязательно для заполнения.")
                input("Нажмите Enter для продолжения...")
                continue
                
            home_arena = input("Домашняя арена: ")
            
            foundation_year_str = input("Год основания (пусто для пропуска): ")
            foundation_year = None
            if foundation_year_str:
                try:
                    foundation_year = int(foundation_year_str)
                except ValueError:
                    print("Некорректный год основания. Используйте целое число.")
                    input("Нажмите Enter для продолжения...")
                    continue
            
            description = input("Описание команды: ")
            
            # Выбор тренера
            print("\nВыберите тренера:")
            users = auth_service.get_all_users()
            print("0. Не назначать тренера")
            for user in users:
                print(f"{user.id}. {user.full_name}")
                
            coach_id_str = input("\nВведите ID тренера (0 для пропуска): ")
            coach_id = None
            if coach_id_str != '0':
                try:
                    coach_id = int(coach_id_str)
                    if not any(user.id == coach_id for user in users):
                        print("Тренер с указанным ID не найден.")
                        input("Нажмите Enter для продолжения...")
                        continue
                except ValueError:
                    print("Некорректный ID тренера. Используйте целое число.")
                    input("Нажмите Enter для продолжения...")
                    continue
            
            is_opponent_str = input("Это команда-соперник? (да/нет): ").lower()
            is_opponent = is_opponent_str in ['да', 'д', 'yes', 'y', '1']
            
            # Создание команды
            team_data = {
                'name': name,
                'home_arena': home_arena,
                'foundation_year': foundation_year,
                'description': description,
                'coach_id': coach_id,
                'is_opponent': is_opponent
            }
            
            team = team_service.create_team(team_data)
            
            if team:
                print(f"\nКоманда '{name}' успешно создана!")
                
                # Предложение добавить игроков в команду
                add_players = input("\nХотите добавить игроков в команду? (да/нет): ").lower()
                if add_players in ['да', 'д', 'yes', 'y', '1']:
                    add_players_to_team(team.id)
            else:
                print("\nНе удалось создать команду. Проверьте введенные данные.")
            
            input("Нажмите Enter для продолжения...")
            
        elif choice == '4':
            print_header("Редактирование команды")
            
            # Выбор команды для редактирования
            teams = team_service.get_all_teams()
            
            if not teams:
                print("Команды не найдены.")
                input("Нажмите Enter для продолжения...")
                continue
                
            print("Доступные команды:")
            for team in teams:
                print(f"{team.id}. {team.name}")
                
            team_id_str = input("\nВведите ID команды для редактирования (0 для отмены): ")
            if team_id_str == '0':
                continue
                
            try:
                team_id = int(team_id_str)
                team = team_service.get_team_by_id(team_id)
                
                if not team:
                    print("Команда с указанным ID не найдена.")
                    input("Нажмите Enter для продолжения...")
                    continue
                    
                print(f"\nРедактирование команды '{team.name}'")
                print("Оставьте поле пустым, чтобы сохранить текущее значение")
                
                name = input(f"Название команды [{team.name}]: ")
                if not name:
                    name = team.name
                    
                home_arena = input(f"Домашняя арена [{team.home_arena or ''}]: ")
                if not home_arena:
                    home_arena = team.home_arena
                    
                foundation_year_str = input(f"Год основания [{team.foundation_year or ''}]: ")
                foundation_year = team.foundation_year
                if foundation_year_str:
                    try:
                        foundation_year = int(foundation_year_str)
                    except ValueError:
                        print("Некорректный год основания. Используется предыдущее значение.")
                
                description = input(f"Описание команды [{team.description or ''}]: ")
                if not description:
                    description = team.description
                
                # Выбор тренера
                print("\nВыберите тренера:")
                users = auth_service.get_all_users()
                current_coach = "Не назначен"
                if team.coach:
                    current_coach = team.coach.full_name
                    
                print(f"Текущий тренер: {current_coach}")
                print("0. Не менять тренера")
                print("1. Убрать тренера")
                for user in users:
                    print(f"{user.id + 1}. {user.full_name}")
                    
                coach_id_str = input("\nВведите ID тренера (0 для пропуска): ")
                coach_id = team.coach_id
                
                if coach_id_str == '1':
                    coach_id = None
                elif coach_id_str != '0':
                    try:
                        selected_id = int(coach_id_str) - 1
                        if selected_id >= 0 and selected_id < len(users):
                            coach_id = users[selected_id].id
                        else:
                            print("Тренер с указанным ID не найден. Используется предыдущее значение.")
                    except ValueError:
                        print("Некорректный ID тренера. Используется предыдущее значение.")
                
                is_opponent_str = input(f"Это команда-соперник? (да/нет) [{'да' if team.is_opponent else 'нет'}]: ").lower()
                is_opponent = team.is_opponent
                if is_opponent_str:
                    is_opponent = is_opponent_str in ['да', 'д', 'yes', 'y', '1']
                
                # Обновление команды
                team_data = {
                    'name': name,
                    'home_arena': home_arena,
                    'foundation_year': foundation_year,
                    'description': description,
                    'coach_id': coach_id,
                    'is_opponent': is_opponent
                }
                
                updated_team = team_service.update_team(team_id, team_data)
                
                if updated_team:
                    print(f"\nКоманда '{name}' успешно обновлена!")
                else:
                    print("\nНе удалось обновить команду. Проверьте введенные данные.")
                
            except ValueError:
                print("Некорректный ID. Введите число.")
            
            input("Нажмите Enter для продолжения...")
            
        elif choice == '5':
            print_header("Удаление команды")
            
            # Выбор команды для удаления
            teams = team_service.get_all_teams()
            
            if not teams:
                print("Команды не найдены.")
                input("Нажмите Enter для продолжения...")
                continue
                
            print("Доступные команды:")
            for team in teams:
                print(f"{team.id}. {team.name}")
                
            team_id_str = input("\nВведите ID команды для удаления (0 для отмены): ")
            if team_id_str == '0':
                continue
                
            try:
                team_id = int(team_id_str)
                team = team_service.get_team_by_id(team_id)
                
                if not team:
                    print("Команда с указанным ID не найдена.")
                    input("Нажмите Enter для продолжения...")
                    continue
                    
                confirm = input(f"Вы уверены, что хотите удалить команду '{team.name}'? (да/нет): ").lower()
                if confirm not in ['да', 'д', 'yes', 'y', '1']:
                    print("Удаление отменено.")
                    input("Нажмите Enter для продолжения...")
                    continue
                    
                success = team_service.delete_team(team_id)
                
                if success:
                    print(f"\nКоманда '{team.name}' успешно удалена!")
                else:
                    print("\nНе удалось удалить команду. Возможно, есть связанные данные.")
                
            except ValueError:
                print("Некорректный ID. Введите число.")
            
            input("Нажмите Enter для продолжения...")
            
        elif choice == '6':
            # Управление турнирами
            tournaments_menu()
            
        elif choice == '7':
            print_header("Экспорт списка команд в Excel")
            
            teams = team_service.get_all_teams()
            
            if not teams:
                print("Нет данных для экспорта.")
                input("Нажмите Enter для продолжения...")
                continue
                
            # Подготовка данных для экспорта
            export_data = []
            for team in teams:
                coach_name = team.coach.full_name if team.coach else "Не назначен"
                export_data.append({
                    'ID': team.id,
                    'Название': team.name,
                    'Домашняя арена': team.home_arena or "",
                    'Год основания': team.foundation_year or "",
                    'Тренер': coach_name,
                    'Соперник': "Да" if team.is_opponent else "Нет",
                    'Описание': team.description or ""
                })
                
            # Экспорт в Excel
            from utils import export_to_excel
            filename = f"teams_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            export_path = export_to_excel(export_data, filename, sheet_name='Команды')
            
            if export_path:
                print(f"Данные успешно экспортированы в файл: {export_path}")
            else:
                print("Не удалось экспортировать данные.")
                
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

def add_players_to_team(team_id):
    """Функция для добавления игроков в команду"""
    from services.player_service import PlayerService
    
    team_service = TeamService()
    player_service = PlayerService()
    
    team = team_service.get_team_by_id(team_id)
    if not team:
        print("Команда не найдена.")
        return
    
    print(f"\nДобавление игроков в команду '{team.name}'")
    
    while True:
        print("\nДоступные позиции:")
        positions = {
            '1': 'вратарь',
            '2': 'защитник',
            '3': 'нападающий',
            '0': 'Завершить добавление игроков'
        }
        print_menu(positions)
        
        position_choice = get_menu_choice(positions)
        
        if position_choice == '0':
            break
        
        position = positions.get(position_choice)
        
        print(f"\nДобавление {position}а в команду")
        
        # Основная информация об игроке
        first_name = input("Имя: ")
        if not first_name:
            print("Имя игрока обязательно для заполнения.")
            continue
        
        last_name = input("Фамилия: ")
        if not last_name:
            print("Фамилия игрока обязательна для заполнения.")
            continue
        
        middle_name = input("Отчество (пусто для пропуска): ")
        
        jersey_number_str = input("Игровой номер: ")
        jersey_number = None
        if jersey_number_str:
            try:
                jersey_number = int(jersey_number_str)
            except ValueError:
                print("Некорректный номер. Используйте целое число.")
                continue
        
        birth_date_str = input("Дата рождения (ДД.ММ.ГГГГ, пусто для пропуска): ")
        birth_date = None
        if birth_date_str:
            try:
                from datetime import datetime
                birth_date = datetime.strptime(birth_date_str, "%d.%m.%Y").date()
            except ValueError:
                print("Некорректный формат даты. Используйте формат ДД.ММ.ГГГГ.")
                continue
        
        height_str = input("Рост (см, пусто для пропуска): ")
        height = None
        if height_str:
            try:
                height = int(height_str)
            except ValueError:
                print("Некорректный рост. Используйте целое число.")
                continue
        
        weight_str = input("Вес (кг, пусто для пропуска): ")
        weight = None
        if weight_str:
            try:
                weight = int(weight_str)
            except ValueError:
                print("Некорректный вес. Используйте целое число.")
                continue
        
        notes = input("Дополнительные заметки: ")
        
        # Создание игрока
        player_data = {
            'first_name': first_name,
            'last_name': last_name,
            'middle_name': middle_name,
            'position': position,
            'jersey_number': jersey_number,
            'birth_date': birth_date,
            'height': height,
            'weight': weight,
            'team_id': team_id,
            'notes': notes,
            'is_active': True
        }
        
        player = player_service.create_player(player_data)
        
        if player:
            print(f"\nИгрок {last_name} {first_name} успешно добавлен в команду!")
        else:
            print("\nНе удалось добавить игрока. Проверьте введенные данные.")
        
        another = input("\nДобавить еще одного игрока? (да/нет): ").lower()
        if another not in ['да', 'д', 'yes', 'y', '1']:
            break
    
    # Вывод обновленного состава команды
    players = team_service.get_team_players(team_id)
    print(f"\nОбновленный состав команды '{team.name}':")
    
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

def tournaments_menu():
    """Меню управления турнирами"""
    options = {
        '1': 'Список турниров',
        '2': 'Информация о турнире',
        '3': 'Добавить турнир',
        '4': 'Редактировать турнир',
        '5': 'Удалить турнир',
        '6': 'Управление командами в турнире',
        '7': 'Экспорт данных в Excel',
        '0': 'Вернуться в главное меню'
    }
    
    team_service = TeamService()
    
    while True:
        print_header("Управление турнирами")
        print_menu(options)
        
        choice = get_menu_choice(options)
        
        if choice == '1':
            print_header("Список турниров")
            
            tournaments = team_service.get_all_tournaments()
            
            if not tournaments:
                print("Турниры не найдены.")
            else:
                headers = ["ID", "Название", "Дата начала", "Дата окончания", "Место проведения"]
                data = []
                
                for tournament in tournaments:
                    data.append([
                        tournament.id,
                        tournament.name,
                        tournament.start_date.strftime("%d.%m.%Y") if tournament.start_date else "Не указана",
                        tournament.end_date.strftime("%d.%m.%Y") if tournament.end_date else "Не указана",
                        tournament.location or "Не указано"
                    ])
                
                print_data_table(headers, data)
            
            input("Нажмите Enter для продолжения...")
            
        elif choice == '2':
            print_header("Информация о турнире")
            
            tournament_id = input("Введите ID турнира (0 для отмены): ")
            if tournament_id == '0':
                continue
            
            try:
                tournament_id = int(tournament_id)
                tournament = team_service.get_tournament_by_id(tournament_id)
                
                if tournament:
                    print(f"Название: {tournament.name}")
                    print(f"Даты проведения: {tournament.start_date.strftime('%d.%m.%Y') if tournament.start_date else 'Не указана'} - "
                          f"{tournament.end_date.strftime('%d.%m.%Y') if tournament.end_date else 'Не указана'}")
                    print(f"Место проведения: {tournament.location or 'Не указано'}")
                    print(f"Описание: {tournament.description or 'Нет описания'}")
                    
                    # Команды-участники
                    tournament_teams = team_service.get_tournament_teams(tournament_id)
                    
                    print("\nКоманды-участники:")
                    if not tournament_teams:
                        print("Нет зарегистрированных команд.")
                    else:
                        headers = ["ID", "Команда", "Место в турнире"]
                        data = []
                        
                        for tt in tournament_teams:
                            team_name = tt.team.name if tt.team else "Неизвестная команда"
                            data.append([
                                tt.id,
                                team_name,
                                tt.rank or "-"
                            ])
                        
                        print_data_table(headers, data)
                else:
                    print("Турнир не найден.")
            except ValueError:
                print("Некорректный ID. Введите число.")
            
            input("Нажмите Enter для продолжения...")
            
        elif choice == '3':
            print_header("Добавление нового турнира")
            
            name = input("Название турнира: ")
            if not name:
                print("Название турнира обязательно для заполнения.")
                input("Нажмите Enter для продолжения...")
                continue
            
            location = input("Место проведения: ")
            
            # Даты проведения
            start_date_str = input("Дата начала (ДД.ММ.ГГГГ): ")
            start_date = None
            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, "%d.%m.%Y").date()
                except ValueError:
                    print("Некорректный формат даты. Используйте формат ДД.ММ.ГГГГ.")
                    input("Нажмите Enter для продолжения...")
                    continue
            
            end_date_str = input("Дата окончания (ДД.ММ.ГГГГ): ")
            end_date = None
            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, "%d.%m.%Y").date()
                except ValueError:
                    print("Некорректный формат даты. Используйте формат ДД.ММ.ГГГГ.")
                    input("Нажмите Enter для продолжения...")
                    continue
            
            description = input("Описание турнира: ")
            
            # Создание турнира
            tournament_data = {
                'name': name,
                'location': location,
                'start_date': start_date,
                'end_date': end_date,
                'description': description
            }
            
            tournament = team_service.create_tournament(tournament_data)
            
            if tournament:
                print(f"\nТурнир '{name}' успешно создан!")
            else:
                print("\nНе удалось создать турнир. Проверьте введенные данные.")
            
            input("Нажмите Enter для продолжения...")
            
        elif choice == '4':
            print_header("Редактирование турнира")
            
            # Выбор турнира для редактирования
            tournaments = team_service.get_all_tournaments()
            
            if not tournaments:
                print("Турниры не найдены.")
                input("Нажмите Enter для продолжения...")
                continue
            
            print("Доступные турниры:")
            for tournament in tournaments:
                print(f"{tournament.id}. {tournament.name}")
            
            tournament_id_str = input("\nВведите ID турнира для редактирования (0 для отмены): ")
            if tournament_id_str == '0':
                continue
            
            try:
                tournament_id = int(tournament_id_str)
                tournament = team_service.get_tournament_by_id(tournament_id)
                
                if not tournament:
                    print("Турнир с указанным ID не найден.")
                    input("Нажмите Enter для продолжения...")
                    continue
                
                print(f"\nРедактирование турнира '{tournament.name}'")
                print("Оставьте поле пустым, чтобы сохранить текущее значение")
                
                name = input(f"Название турнира [{tournament.name}]: ")
                if not name:
                    name = tournament.name
                
                location = input(f"Место проведения [{tournament.location or ''}]: ")
                if not location:
                    location = tournament.location
                
                # Даты проведения
                current_start = tournament.start_date.strftime("%d.%m.%Y") if tournament.start_date else ""
                start_date_str = input(f"Дата начала (ДД.ММ.ГГГГ) [{current_start}]: ")
                start_date = tournament.start_date
                if start_date_str:
                    try:
                        start_date = datetime.strptime(start_date_str, "%d.%m.%Y").date()
                    except ValueError:
                        print("Некорректный формат даты. Используется предыдущее значение.")
                
                current_end = tournament.end_date.strftime("%d.%m.%Y") if tournament.end_date else ""
                end_date_str = input(f"Дата окончания (ДД.ММ.ГГГГ) [{current_end}]: ")
                end_date = tournament.end_date
                if end_date_str:
                    try:
                        end_date = datetime.strptime(end_date_str, "%d.%m.%Y").date()
                    except ValueError:
                        print("Некорректный формат даты. Используется предыдущее значение.")
                
                description = input(f"Описание турнира [{tournament.description or ''}]: ")
                if not description:
                    description = tournament.description
                
                # Обновление турнира
                tournament_data = {
                    'name': name,
                    'location': location,
                    'start_date': start_date,
                    'end_date': end_date,
                    'description': description
                }
                
                updated_tournament = team_service.update_tournament(tournament_id, tournament_data)
                
                if updated_tournament:
                    print(f"\nТурнир '{name}' успешно обновлен!")
                else:
                    print("\nНе удалось обновить турнир. Проверьте введенные данные.")
                
            except ValueError:
                print("Некорректный ID. Введите число.")
            
            input("Нажмите Enter для продолжения...")
            
        elif choice == '5':
            print_header("Удаление турнира")
            
            # Выбор турнира для удаления
            tournaments = team_service.get_all_tournaments()
            
            if not tournaments:
                print("Турниры не найдены.")
                input("Нажмите Enter для продолжения...")
                continue
            
            print("Доступные турниры:")
            for tournament in tournaments:
                print(f"{tournament.id}. {tournament.name}")
            
            tournament_id_str = input("\nВведите ID турнира для удаления (0 для отмены): ")
            if tournament_id_str == '0':
                continue
            
            try:
                tournament_id = int(tournament_id_str)
                tournament = team_service.get_tournament_by_id(tournament_id)
                
                if not tournament:
                    print("Турнир с указанным ID не найден.")
                    input("Нажмите Enter для продолжения...")
                    continue
                
                confirm = input(f"Вы уверены, что хотите удалить турнир '{tournament.name}'? (да/нет): ").lower()
                if confirm not in ['да', 'д', 'yes', 'y', '1']:
                    print("Удаление отменено.")
                    input("Нажмите Enter для продолжения...")
                    continue
                
                success = team_service.delete_tournament(tournament_id)
                
                if success:
                    print(f"\nТурнир '{tournament.name}' успешно удален!")
                else:
                    print("\nНе удалось удалить турнир. Возможно, есть связанные данные.")
                
            except ValueError:
                print("Некорректный ID. Введите число.")
            
            input("Нажмите Enter для продолжения...")
            
        elif choice == '6':
            print_header("Управление командами в турнире")
            
            # Выбор турнира
            tournaments = team_service.get_all_tournaments()
            
            if not tournaments:
                print("Турниры не найдены.")
                input("Нажмите Enter для продолжения...")
                continue
            
            print("Выберите турнир:")
            for tournament in tournaments:
                print(f"{tournament.id}. {tournament.name}")
            
            tournament_id_str = input("\nВведите ID турнира (0 для отмены): ")
            if tournament_id_str == '0':
                continue
            
            try:
                tournament_id = int(tournament_id_str)
                tournament = team_service.get_tournament_by_id(tournament_id)
                
                if not tournament:
                    print("Турнир с указанным ID не найден.")
                    input("Нажмите Enter для продолжения...")
                    continue
                
                # Подменю управления командами в турнире
                tournament_teams_menu(tournament_id)
                
            except ValueError:
                print("Некорректный ID. Введите число.")
            
            input("Нажмите Enter для продолжения...")
            
        elif choice == '7':
            print_header("Экспорт данных в Excel")
            
            tournaments = team_service.get_all_tournaments()
            
            if not tournaments:
                print("Нет данных для экспорта.")
                input("Нажмите Enter для продолжения...")
                continue
            
            # Подготовка данных для экспорта
            export_data = []
            for tournament in tournaments:
                export_data.append({
                    'ID': tournament.id,
                    'Название': tournament.name,
                    'Дата начала': tournament.start_date.strftime("%d.%m.%Y") if tournament.start_date else "",
                    'Дата окончания': tournament.end_date.strftime("%d.%m.%Y") if tournament.end_date else "",
                    'Место проведения': tournament.location or "",
                    'Описание': tournament.description or ""
                })
            
            # Экспорт в Excel
            from utils import export_to_excel
            filename = f"tournaments_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            export_path = export_to_excel(export_data, filename, sheet_name='Турниры')
            
            if export_path:
                print(f"Данные успешно экспортированы в файл: {export_path}")
            else:
                print("Не удалось экспортировать данные.")
            
            input("Нажмите Enter для продолжения...")
            
        elif choice == '0':
            break

def tournament_teams_menu(tournament_id):
    """Меню управления командами в турнире"""
    options = {
        '1': 'Список команд в турнире',
        '2': 'Добавить команду в турнир',
        '3': 'Удалить команду из турнира',
        '4': 'Обновить место команды в турнире',
        '0': 'Вернуться в меню турниров'
    }
    
    team_service = TeamService()
    tournament = team_service.get_tournament_by_id(tournament_id)
    
    if not tournament:
        print("Турнир не найден.")
        return
    
    while True:
        print_header(f"Управление командами в турнире '{tournament.name}'")
        print_menu(options)
        
        choice = get_menu_choice(options)
        
        if choice == '1':
            print_header(f"Список команд в турнире '{tournament.name}'")
            
            tournament_teams = team_service.get_tournament_teams(tournament_id)
            
            if not tournament_teams:
                print("В турнире нет зарегистрированных команд.")
            else:
                headers = ["ID", "Команда", "Место в турнире"]
                data = []
                
                for tt in tournament_teams:
                    team_name = tt.team.name if tt.team else "Неизвестная команда"
                    data.append([
                        tt.id,
                        team_name,
                        tt.rank or "-"
                    ])
                
                print_data_table(headers, data)
            
            input("Нажмите Enter для продолжения...")
            
        elif choice == '2':
            print_header(f"Добавление команды в турнир '{tournament.name}'")
            
            # Получение списка команд, не участвующих в турнире
            available_teams = team_service.get_available_teams_for_tournament(tournament_id)
            
            if not available_teams:
                print("Нет доступных команд для добавления в турнир.")
                input("Нажмите Enter для продолжения...")
                continue
            
            print("Доступные команды:")
            for team in available_teams:
                print(f"{team.id}. {team.name}")
            
            team_id_str = input("\nВведите ID команды для добавления (0 для отмены): ")
            if team_id_str == '0':
                continue
            
            try:
                team_id = int(team_id_str)
                if not any(team.id == team_id for team in available_teams):
                    print("Команда с указанным ID не найдена среди доступных.")
                    input("Нажмите Enter для продолжения...")
                    continue
                
                rank_str = input("Введите место команды в турнире (пусто, если не известно): ")
                rank = None
                if rank_str:
                    try:
                        rank = int(rank_str)
                    except ValueError:
                        print("Некорректный формат места. Используется пустое значение.")
                
                # Добавление команды в турнир
                data = {
                    'tournament_id': tournament_id,
                    'team_id': team_id,
                    'rank': rank
                }
                
                tournament_team = team_service.add_team_to_tournament(data)
                
                if tournament_team:
                    team_name = tournament_team.team.name if tournament_team.team else f"Команда #{team_id}"
                    print(f"\nКоманда '{team_name}' успешно добавлена в турнир!")
                else:
                    print("\nНе удалось добавить команду в турнир. Проверьте введенные данные.")
                
            except ValueError:
                print("Некорректный ID. Введите число.")
            
            input("Нажмите Enter для продолжения...")
            
        elif choice == '3':
            print_header(f"Удаление команды из турнира '{tournament.name}'")
            
            # Получение списка команд в турнире
            tournament_teams = team_service.get_tournament_teams(tournament_id)
            
            if not tournament_teams:
                print("В турнире нет зарегистрированных команд.")
                input("Нажмите Enter для продолжения...")
                continue
            
            print("Команды в турнире:")
            for tt in tournament_teams:
                team_name = tt.team.name if tt.team else "Неизвестная команда"
                print(f"{tt.id}. {team_name}")
            
            tt_id_str = input("\nВведите ID записи для удаления (0 для отмены): ")
            if tt_id_str == '0':
                continue
            
            try:
                tt_id = int(tt_id_str)
                if not any(tt.id == tt_id for tt in tournament_teams):
                    print("Запись с указанным ID не найдена.")
                    input("Нажмите Enter для продолжения...")
                    continue
                
                # Найдем команду для отображения
                selected_tt = next((tt for tt in tournament_teams if tt.id == tt_id), None)
                team_name = selected_tt.team.name if selected_tt and selected_tt.team else f"Запись #{tt_id}"
                
                confirm = input(f"Вы уверены, что хотите удалить команду '{team_name}' из турнира? (да/нет): ").lower()
                if confirm not in ['да', 'д', 'yes', 'y', '1']:
                    print("Удаление отменено.")
                    input("Нажмите Enter для продолжения...")
                    continue
                
                success = team_service.remove_team_from_tournament(tt_id)
                
                if success:
                    print(f"\nКоманда '{team_name}' успешно удалена из турнира!")
                else:
                    print("\nНе удалось удалить команду из турнира.")
                
            except ValueError:
                print("Некорректный ID. Введите число.")
            
            input("Нажмите Enter для продолжения...")
            
        elif choice == '4':
            print_header(f"Обновление места команды в турнире '{tournament.name}'")
            
            # Получение списка команд в турнире
            tournament_teams = team_service.get_tournament_teams(tournament_id)
            
            if not tournament_teams:
                print("В турнире нет зарегистрированных команд.")
                input("Нажмите Enter для продолжения...")
                continue
            
            print("Команды в турнире:")
            for tt in tournament_teams:
                team_name = tt.team.name if tt.team else "Неизвестная команда"
                rank = tt.rank or "Не определено"
                print(f"{tt.id}. {team_name} (Текущее место: {rank})")
            
            tt_id_str = input("\nВведите ID записи для обновления (0 для отмены): ")
            if tt_id_str == '0':
                continue
            
            try:
                tt_id = int(tt_id_str)
                if not any(tt.id == tt_id for tt in tournament_teams):
                    print("Запись с указанным ID не найдена.")
                    input("Нажмите Enter для продолжения...")
                    continue
                
                # Найдем команду для отображения
                selected_tt = next((tt for tt in tournament_teams if tt.id == tt_id), None)
                team_name = selected_tt.team.name if selected_tt and selected_tt.team else f"Запись #{tt_id}"
                current_rank = selected_tt.rank if selected_tt else None
                
                rank_str = input(f"Введите новое место команды в турнире [{current_rank or 'Не определено'}]: ")
                if not rank_str:
                    if current_rank is not None:
                        print("Место не изменено.")
                        input("Нажмите Enter для продолжения...")
                        continue
                    else:
                        rank = None
                else:
                    try:
                        rank = int(rank_str)
                    except ValueError:
                        print("Некорректный формат места. Используется предыдущее значение.")
                        input("Нажмите Enter для продолжения...")
                        continue
                
                success = team_service.update_team_rank(tt_id, rank)
                
                if success:
                    new_rank_str = rank if rank is not None else "не определено"
                    print(f"\nМесто команды '{team_name}' успешно обновлено на {new_rank_str}!")
                else:
                    print("\nНе удалось обновить место команды.")
                
            except ValueError:
                print("Некорректный ID. Введите число.")
            
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