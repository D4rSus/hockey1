# -*- coding: utf-8 -*-

"""
Модели данных для приложения
"""

import os
import datetime
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Float, ForeignKey, Text, Time
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash

from database import Base

class User(Base):
    """Модель пользователя (тренера)"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100))
    phone = Column(String(20))
    created_at = Column(DateTime, default=datetime.datetime.now)
    last_login = Column(DateTime)
    is_admin = Column(Boolean, default=False)
    
    def set_password(self, password):
        """Установка пароля пользователя"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Проверка пароля пользователя"""
        return check_password_hash(self.password_hash, password)

class Team(Base):
    """Модель команды"""
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    logo_path = Column(String(200))
    description = Column(Text)
    foundation_year = Column(Integer)
    home_arena = Column(String(100))
    coach_id = Column(Integer, ForeignKey('users.id'))
    is_opponent = Column(Boolean, default=False)
    
    # Отношения
    coach = relationship("User", foreign_keys=[coach_id])
    players = relationship("Player", back_populates="team")
    home_matches = relationship("Match", foreign_keys="Match.home_team_id", back_populates="home_team")
    away_matches = relationship("Match", foreign_keys="Match.away_team_id", back_populates="away_team")
    trainings = relationship("Training", back_populates="team")
    stats = relationship("TeamStats", back_populates="team")

class Player(Base):
    """Модель игрока"""
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    middle_name = Column(String(50))
    birth_date = Column(Date)
    position = Column(String(20), nullable=False)  # нападающий, защитник, вратарь
    jersey_number = Column(Integer)
    height = Column(Integer)  # в см
    weight = Column(Integer)  # в кг
    photo_path = Column(String(200))
    team_id = Column(Integer, ForeignKey('teams.id'))
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    
    # Отношения
    team = relationship("Team", back_populates="players")
    stats = relationship("PlayerStats", back_populates="player")
    attendances = relationship("Attendance", back_populates="player")
    
    @hybrid_property
    def full_name(self):
        """Полное имя игрока"""
        if self.middle_name:
            return f"{self.last_name} {self.first_name} {self.middle_name}"
        return f"{self.last_name} {self.first_name}"
    
    @hybrid_property
    def age(self):
        """Возраст игрока"""
        if self.birth_date:
            today = datetime.date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None

class PlayerStats(Base):
    """Модель статистики игрока"""
    __tablename__ = 'player_stats'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    match_id = Column(Integer, ForeignKey('matches.id'))
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    penalty_minutes = Column(Integer, default=0)
    plus_minus = Column(Integer, default=0)
    shots = Column(Integer, default=0)
    time_on_ice = Column(Integer, default=0)  # в секундах
    faceoffs_won = Column(Integer, default=0)
    faceoffs_total = Column(Integer, default=0)
    
    # Отношения
    player = relationship("Player", back_populates="stats")
    match = relationship("Match", back_populates="player_stats")
    
    @hybrid_property
    def points(self):
        """Сумма очков (гол + пас)"""
        return self.goals + self.assists
    
    @hybrid_property
    def faceoff_percentage(self):
        """Процент выигранных вбрасываний"""
        if self.faceoffs_total == 0:
            return 0
        return (self.faceoffs_won / self.faceoffs_total) * 100

class TeamStats(Base):
    """Модель статистики команды"""
    __tablename__ = 'team_stats'
    
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    match_id = Column(Integer, ForeignKey('matches.id'))
    goals_for = Column(Integer, default=0)
    goals_against = Column(Integer, default=0)
    shots_for = Column(Integer, default=0)
    shots_against = Column(Integer, default=0)
    penalty_minutes = Column(Integer, default=0)
    powerplay_goals = Column(Integer, default=0)
    powerplay_opportunities = Column(Integer, default=0)
    shorthanded_goals_for = Column(Integer, default=0)
    shorthanded_goals_against = Column(Integer, default=0)
    
    # Отношения
    team = relationship("Team", back_populates="stats")
    match = relationship("Match", back_populates="team_stats")
    
    @hybrid_property
    def powerplay_percentage(self):
        """Процент реализации большинства"""
        if self.powerplay_opportunities == 0:
            return 0
        return (self.powerplay_goals / self.powerplay_opportunities) * 100

class Match(Base):
    """Модель матча"""
    __tablename__ = 'matches'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    time = Column(Time)
    home_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    away_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    location = Column(String(100))
    home_score = Column(Integer)
    away_score = Column(Integer)
    status = Column(String(20), default="запланирован")  # запланирован, завершен, отменен
    notes = Column(Text)
    video_path = Column(String(200))
    
    # Отношения
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    player_stats = relationship("PlayerStats", back_populates="match")
    team_stats = relationship("TeamStats", back_populates="match")
    
    @hybrid_property
    def is_completed(self):
        """Проверка, завершен ли матч"""
        return self.status == "завершен"

class Training(Base):
    """Модель тренировки"""
    __tablename__ = 'trainings'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    location = Column(String(100))
    description = Column(Text)
    focus_area = Column(String(100))  # физическая подготовка, тактика, и т.д.
    video_path = Column(String(200))
    
    # Отношения
    team = relationship("Team", back_populates="trainings")
    attendances = relationship("Attendance", back_populates="training")
    exercises = relationship("TrainingExercise", back_populates="training")

class TrainingExercise(Base):
    """Модель упражнения для тренировки"""
    __tablename__ = 'training_exercises'
    
    id = Column(Integer, primary_key=True)
    training_id = Column(Integer, ForeignKey('trainings.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    duration = Column(Integer)  # в минутах
    order = Column(Integer)  # порядок упражнения в тренировке
    
    # Отношения
    training = relationship("Training", back_populates="exercises")

class Attendance(Base):
    """Модель посещаемости"""
    __tablename__ = 'attendances'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    training_id = Column(Integer, ForeignKey('trainings.id'), nullable=False)
    is_present = Column(Boolean, default=False)
    reason = Column(String(200))  # причина отсутствия
    
    # Отношения
    player = relationship("Player", back_populates="attendances")
    training = relationship("Training", back_populates="attendances")

class Tournament(Base):
    """Модель турнира"""
    __tablename__ = 'tournaments'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    location = Column(String(100))
    description = Column(Text)
    
    # Отношения
    participants = relationship("TournamentTeam", back_populates="tournament")

class TournamentTeam(Base):
    """Модель связи турнира и команды"""
    __tablename__ = 'tournament_teams'
    
    id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey('tournaments.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    rank = Column(Integer)  # место в турнире
    
    # Отношения
    tournament = relationship("Tournament", back_populates="participants")
    team = relationship("Team")

class Video(Base):
    """Модель видеоматериала"""
    __tablename__ = 'videos'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    file_path = Column(String(200), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.datetime.now)
    description = Column(Text)
    type = Column(String(20))  # тренировка, матч, анализ
    match_id = Column(Integer, ForeignKey('matches.id'))
    training_id = Column(Integer, ForeignKey('trainings.id'))
    
    # Отношения
    match = relationship("Match")
    training = relationship("Training")
