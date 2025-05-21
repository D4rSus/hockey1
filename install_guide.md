# Руководство по установке приложения "Рабочее место тренера хоккейной команды"

## Системные требования

- **Операционная система**: Windows 10/11, macOS 10.15+, Linux (Ubuntu 20.04+, Fedora 34+)
- **Python**: версия 3.10 или выше
- **Оперативная память**: минимум 4 ГБ (рекомендуется 8 ГБ)
- **Свободное место на диске**: минимум 200 МБ для приложения и зависимостей

## Подготовка окружения

### Установка Python

1. **Windows**:
   - Скачайте установщик Python с [официального сайта](https://www.python.org/downloads/)
   - Запустите установщик и установите флажок "Add Python to PATH"
   - Завершите установку

2. **macOS**:
   - Установите через Homebrew: `brew install python`
   - Или скачайте установщик с [официального сайта](https://www.python.org/downloads/)

3. **Linux**:
   - Ubuntu/Debian: `sudo apt install python3 python3-pip python3-venv`
   - Fedora: `sudo dnf install python3 python3-pip`

### Подготовка базы данных

#### Вариант 1: SQLite (простой и быстрый способ)
SQLite не требует отдельной установки и настройки, база данных будет создана автоматически при первом запуске приложения.

#### Вариант 2: PostgreSQL (рекомендуется для больших команд)

1. **Установка PostgreSQL**:
   - **Windows**: Скачайте и установите [PostgreSQL](https://www.postgresql.org/download/windows/)
   - **macOS**: `brew install postgresql`
   - **Linux**: `sudo apt install postgresql postgresql-contrib` (Ubuntu) или `sudo dnf install postgresql` (Fedora)

2. **Создание базы данных**:
   ```sql
   CREATE DATABASE hockey_coach;
   CREATE USER hockey_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE hockey_coach TO hockey_user;
   ```

## Установка приложения

1. **Клонирование репозитория**:
   ```bash
   git clone <URL репозитория>
   cd hockey-coach-app
   ```

2. **Создание виртуального окружения**:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Установка зависимостей**:
   ```bash
   # Windows
   pip install PyQt5 SQLAlchemy matplotlib pandas numpy psycopg2-binary werkzeug

   # macOS/Linux
   pip3 install PyQt5 SQLAlchemy matplotlib pandas numpy psycopg2-binary werkzeug
   ```

4. **Настройка конфигурации** (если используете PostgreSQL):
   Отредактируйте файл `config.py`, изменив параметр `DB_URI`:
   ```python
   # Замените следующую строку
   DB_URI = f"sqlite:///{DB_PATH}"

   # На строку подключения к PostgreSQL
   DB_URI = "postgresql://hockey_user:your_secure_password@localhost/hockey_coach"
   ```

## Первый запуск приложения

1. **Инициализация базы данных**:
   ```bash
   # Инициализация базы данных и создание демонстрационных данных
   python simple_app.py
   ```

2. **Запуск основного приложения**:
   ```bash
   # Запуск десктопного приложения
   python main.py
   ```

3. **Вход в систему**:
   - Логин: `admin`
   - Пароль: `admin`

## Решение проблем при установке

### Проблемы с PyQt5

**Проблема**: Ошибка установки PyQt5 через pip
**Решение**: 
- Windows: `pip install pyqt5-tools`
- Linux: Установите системные зависимости `sudo apt-get install python3-pyqt5` или `sudo dnf install python3-qt5`
- macOS: `brew install pyqt5`

### Проблемы с psycopg2

**Проблема**: Ошибка при установке psycopg2
**Решение**:
- Windows: Убедитесь, что PostgreSQL установлен и его bin директория добавлена в PATH
- Linux: Установите зависимости `sudo apt-get install libpq-dev python3-dev` или `sudo dnf install postgresql-devel python3-devel`
- macOS: `brew install postgresql`

### Проблемы с запуском

**Проблема**: Не запускается приложение
**Решение**:
1. Проверьте установку всех зависимостей
2. Проверьте путь к Python в вашем окружении
3. Убедитесь, что вы активировали виртуальное окружение
4. Проверьте подключение к базе данных

## Дополнительные настройки

### Настройка каталогов для медиа-файлов

По умолчанию, приложение создает следующие каталоги в корне проекта:
- `media/photos` - для фотографий игроков
- `media/videos` - для видеозаписей матчей и тренировок
- `exports` - для экспортированных отчетов

Вы можете изменить пути в файле `config.py`.

### Настройка логгирования

Для изменения уровня логирования и других параметров отредактируйте параметры 
`LOG_LEVEL` и `LOG_FILE` в файле `config.py`.

## Запуск в консольном режиме

Если вы работаете на сервере без графического интерфейса, используйте консольную версию:

```bash
python console_app.py
```

Эта версия предоставляет доступ ко всем функциям через текстовое меню.