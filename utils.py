# -*- coding: utf-8 -*-

"""
Вспомогательные функции и утилиты
"""

import os
import datetime
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QDateTime, QDate, QTime

from config import Config

def show_error_message(parent, title, message):
    """Показать сообщение об ошибке"""
    QMessageBox.critical(parent, title, message)

def show_info_message(parent, title, message):
    """Показать информационное сообщение"""
    QMessageBox.information(parent, title, message)

def show_question_message(parent, title, message):
    """Показать вопросительное сообщение"""
    return QMessageBox.question(
        parent, 
        title, 
        message, 
        QMessageBox.Yes | QMessageBox.No
    ) == QMessageBox.Yes

def format_date(date):
    """Форматирование даты"""
    if isinstance(date, datetime.date):
        return date.strftime("%d.%m.%Y")
    return ""

def format_time(time):
    """Форматирование времени"""
    if isinstance(time, datetime.time):
        return time.strftime("%H:%M")
    return ""

def format_datetime(dt):
    """Форматирование даты и времени"""
    if isinstance(dt, datetime.datetime):
        return dt.strftime("%d.%m.%Y %H:%M")
    return ""

def date_to_qdate(date):
    """Преобразование даты Python в QDate"""
    if isinstance(date, datetime.date):
        return QDate(date.year, date.month, date.day)
    return QDate.currentDate()

def time_to_qtime(time):
    """Преобразование времени Python в QTime"""
    if isinstance(time, datetime.time):
        return QTime(time.hour, time.minute)
    return QTime.currentTime()

def qdate_to_date(qdate):
    """Преобразование QDate в дату Python"""
    return datetime.date(qdate.year(), qdate.month(), qdate.day())

def qtime_to_time(qtime):
    """Преобразование QTime во время Python"""
    return datetime.time(qtime.hour(), qtime.minute())

def export_to_excel(data, filename, sheet_name='Данные'):
    """Экспорт данных в Excel файл"""
    try:
        # Убедимся, что директория существует
        os.makedirs(Config.EXPORTS_DIR, exist_ok=True)
        
        full_path = os.path.join(Config.EXPORTS_DIR, filename)
        df = pd.DataFrame(data)
        df.to_excel(full_path, sheet_name=sheet_name, index=False)
        print(f"Данные успешно экспортированы в файл: {full_path}")
        return full_path
    except Exception as e:
        print(f"Ошибка при экспорте данных в Excel: {str(e)}")
        return None
        
def import_from_excel(filename, sheet_name=0):
    """Импорт данных из Excel файла
    
    Args:
        filename (str): Путь к файлу Excel
        sheet_name (str or int): Имя или индекс листа для импорта
        
    Returns:
        list: Список словарей с данными из файла
    """
    try:
        if not os.path.exists(filename):
            print(f"Файл не найден: {filename}")
            return []
            
        df = pd.read_excel(filename, sheet_name=sheet_name)
        # Преобразование DataFrame в список словарей
        records = df.to_dict('records')
        print(f"Импортировано {len(records)} записей из файла {filename}")
        return records
    except Exception as e:
        print(f"Ошибка при импорте данных из Excel: {str(e)}")
        return []

def generate_chart(data, chart_type='bar', title='График', xlabel='X', ylabel='Y'):
    """Генерация графика с помощью matplotlib"""
    fig = Figure(figsize=(10, 6), dpi=100)
    ax = fig.add_subplot(111)
    
    if chart_type == 'bar':
        ax.bar(data['labels'], data['values'])
    elif chart_type == 'line':
        ax.plot(data['labels'], data['values'])
    elif chart_type == 'pie':
        ax.pie(data['values'], labels=data['labels'], autopct='%1.1f%%')
        ax.axis('equal')
    
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    
    fig.tight_layout()
    
    canvas = FigureCanvas(fig)
    return canvas

def get_player_photo_path(player_id, filename):
    """Получение пути к фотографии игрока"""
    photo_dir = os.path.join(Config.PHOTOS_DIR, f"player_{player_id}")
    os.makedirs(photo_dir, exist_ok=True)
    return os.path.join(photo_dir, filename)

def get_video_path(video_type, related_id, filename):
    """Получение пути к видеофайлу"""
    video_dir = os.path.join(Config.VIDEO_DIR, f"{video_type}_{related_id}")
    os.makedirs(video_dir, exist_ok=True)
    return os.path.join(video_dir, filename)

def get_unique_filename(directory, base_filename):
    """Получение уникального имени файла"""
    filename, extension = os.path.splitext(base_filename)
    counter = 1
    new_filename = base_filename
    
    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{filename}_{counter}{extension}"
        counter += 1
    
    return new_filename

def validate_required_fields(fields_dict):
    """Проверка обязательных полей"""
    for field_name, field_value in fields_dict.items():
        if not field_value:
            return False, f"Поле '{field_name}' обязательно для заполнения"
    return True, ""
