# -*- coding: utf-8 -*-

"""
Модуль конфигурации приложения
"""

import os
import json
from pathlib import Path

class Config:
    """Класс конфигурации приложения"""
    
    # Основные настройки
    APP_NAME = "Рабочее место тренера хоккейной команды"
    VERSION = "1.0.0"
    
    # Настройки базы данных
    DB_PATH = "hockey_coach.db"
    DB_URI = f"sqlite:///{DB_PATH}"
    
    # Пути к директориям
    BASE_DIR = Path(__file__).parent
    RESOURCES_DIR = BASE_DIR / "resources"
    MEDIA_DIR = BASE_DIR / "media"
    VIDEO_DIR = MEDIA_DIR / "videos"
    PHOTOS_DIR = MEDIA_DIR / "photos"
    EXPORTS_DIR = BASE_DIR / "exports"
    
    # Настройки логирования
    LOG_LEVEL = "INFO"
    LOG_FILE = BASE_DIR / "app.log"
    
    @classmethod
    def init(cls):
        """Инициализация конфигурации"""
        # Создание необходимых директорий, если они не существуют
        for directory in [cls.MEDIA_DIR, cls.VIDEO_DIR, cls.PHOTOS_DIR, cls.EXPORTS_DIR]:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def get_full_path(cls, relative_path):
        """Получение полного пути"""
        return cls.BASE_DIR / relative_path
