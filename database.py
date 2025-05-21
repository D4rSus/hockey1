# -*- coding: utf-8 -*-

"""
Модуль для работы с базой данных
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from config import Config

# Создаем базовый класс для моделей
Base = declarative_base()

# Создаем движок SQLAlchemy
engine = create_engine(Config.DB_URI, echo=False)

# Создаем фабрику сессий
session_factory = sessionmaker(bind=engine)

# Создаем сессию с областью видимости
Session = scoped_session(session_factory)

def get_session():
    """Получение сессии для работы с базой данных"""
    return Session()

def init_db():
    """Инициализация базы данных"""
    # Импортируем модели для создания таблиц
    from models import User, Player, Team, Training, Match, PlayerStats, TeamStats, Attendance
    
    # Создаем директорию для базы данных, если она не существует
    os.makedirs(os.path.dirname(os.path.abspath(Config.DB_PATH)), exist_ok=True)
    
    # Создаем таблицы
    Base.metadata.create_all(engine)
    
    # Создаем сессию
    session = get_session()
    
    # Проверяем, есть ли пользователи, и если нет, создаем администратора
    user_count = session.query(User).count()
    if user_count == 0:
        admin = User(
            username="admin",
            full_name="Администратор",
            is_admin=True
        )
        admin.set_password("admin")
        session.add(admin)
        session.commit()
    
    # Закрываем сессию
    session.close()
