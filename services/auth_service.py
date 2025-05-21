# -*- coding: utf-8 -*-

"""
Сервис для авторизации пользователей
"""

import datetime
from database import get_session
from models import User
from utils import show_error_message

class AuthService:
    """Сервис для работы с авторизацией"""
    
    def __init__(self):
        """Инициализация сервиса"""
        self.session = get_session()
    
    def authenticate(self, username, password):
        """
        Аутентификация пользователя
        
        Args:
            username (str): Имя пользователя
            password (str): Пароль
            
        Returns:
            User: Объект пользователя при успешной аутентификации, None в противном случае
        """
        try:
            # Поиск пользователя по имени
            user = self.session.query(User).filter(User.username == username).first()
            
            # Проверка пароля, если пользователь найден
            if user and user.check_password(password):
                # Обновление времени последнего входа
                user.last_login = datetime.datetime.now()
                self.session.commit()
                return user
            
            return None
        except Exception as e:
            print(f"Ошибка при аутентификации: {str(e)}")
            self.session.rollback()
            return None
    
    def register_user(self, username, password, full_name, email=None, phone=None, is_admin=False):
        """
        Регистрация нового пользователя
        
        Args:
            username (str): Имя пользователя
            password (str): Пароль
            full_name (str): Полное имя
            email (str, optional): Email. Defaults to None.
            phone (str, optional): Телефон. Defaults to None.
            is_admin (bool, optional): Флаг администратора. Defaults to False.
            
        Returns:
            User: Созданный пользователь или None в случае ошибки
        """
        try:
            # Проверка наличия пользователя с таким именем
            existing_user = self.session.query(User).filter(User.username == username).first()
            if existing_user:
                return None
            
            # Создание нового пользователя
            user = User(
                username=username,
                full_name=full_name,
                email=email,
                phone=phone,
                is_admin=is_admin,
                created_at=datetime.datetime.now()
            )
            user.set_password(password)
            
            # Сохранение пользователя
            self.session.add(user)
            self.session.commit()
            
            return user
        except Exception as e:
            print(f"Ошибка при регистрации пользователя: {str(e)}")
            self.session.rollback()
            return None
    
    def change_password(self, user_id, old_password, new_password):
        """
        Изменение пароля пользователя
        
        Args:
            user_id (int): ID пользователя
            old_password (str): Старый пароль
            new_password (str): Новый пароль
            
        Returns:
            bool: True при успешном изменении, False в противном случае
        """
        try:
            # Поиск пользователя
            user = self.session.query(User).filter(User.id == user_id).first()
            
            # Проверка старого пароля
            if not user or not user.check_password(old_password):
                return False
            
            # Установка нового пароля
            user.set_password(new_password)
            self.session.commit()
            
            return True
        except Exception as e:
            print(f"Ошибка при изменении пароля: {str(e)}")
            self.session.rollback()
            return False
    
    def get_user_by_id(self, user_id):
        """
        Получение пользователя по ID
        
        Args:
            user_id (int): ID пользователя
            
        Returns:
            User: Объект пользователя или None, если пользователь не найден
        """
        try:
            return self.session.query(User).filter(User.id == user_id).first()
        except Exception as e:
            print(f"Ошибка при получении пользователя: {str(e)}")
            return None
    
    def update_user_profile(self, user_id, full_name=None, email=None, phone=None):
        """
        Обновление профиля пользователя
        
        Args:
            user_id (int): ID пользователя
            full_name (str, optional): Полное имя. Defaults to None.
            email (str, optional): Email. Defaults to None.
            phone (str, optional): Телефон. Defaults to None.
            
        Returns:
            bool: True при успешном обновлении, False в противном случае
        """
        try:
            # Поиск пользователя
            user = self.session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False
            
            # Обновление данных
            if full_name is not None:
                user.full_name = full_name
            
            if email is not None:
                user.email = email
            
            if phone is not None:
                user.phone = phone
            
            self.session.commit()
            
            return True
        except Exception as e:
            print(f"Ошибка при обновлении профиля: {str(e)}")
            self.session.rollback()
            return False
    
    def get_all_users(self):
        """
        Получение списка всех пользователей
        
        Returns:
            list: Список пользователей
        """
        try:
            return self.session.query(User).all()
        except Exception as e:
            print(f"Ошибка при получении списка пользователей: {str(e)}")
            return []
    
    def delete_user(self, user_id):
        """
        Удаление пользователя
        
        Args:
            user_id (int): ID пользователя
            
        Returns:
            bool: True при успешном удалении, False в противном случае
        """
        try:
            # Поиск пользователя
            user = self.session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False
            
            # Удаление пользователя
            self.session.delete(user)
            self.session.commit()
            
            return True
        except Exception as e:
            print(f"Ошибка при удалении пользователя: {str(e)}")
            self.session.rollback()
            return False

