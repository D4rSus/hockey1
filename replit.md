# Hockey Coach Application Architecture Guide

## Overview

This application is designed as a comprehensive management system for hockey coaches. It provides functionality for managing player rosters, tracking team and player statistics, scheduling training sessions and matches, and analyzing performance data. The application uses a PyQt5-based desktop interface with SQLAlchemy for database operations, and includes features for visualization through matplotlib.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a layered architecture with distinct separation between:

1. **UI Layer** - PyQt5-based interface components in the `ui/` directory
2. **Service Layer** - Business logic in the `services/` directory
3. **Data Layer** - Database models and operations using SQLAlchemy
4. **Utility Layer** - Helper functions and utilities in `utils.py`

The application is configured to use SQLite as the database backend, with paths specified in `config.py`. All modules use UTF-8 encoding and are written in Russian, which might require consideration when extending the codebase.

## Key Components

### Data Models (models.py)

The data model consists of several key entities:

- **User**: Represents system users (coaches) with authentication capabilities
- **Team**: Represents hockey teams, can be either the coached team or opponents
- **Player**: Represents hockey players with personal and performance data
- **Training**: Represents training sessions
- **Match**: Represents matches between teams
- **Player/TeamStats**: Tracks statistical data for players and teams
- **Attendance**: Tracks player attendance at training sessions

The models use SQLAlchemy's declarative system with relationships between entities.

### UI Components (ui/)

The application uses a multi-window interface with:

- **Login/Auth System**: User authentication via username/password
- **Main Window**: Central navigation hub with tabs for different features
- **Player Management**: View and edit player details, photos, and statistics
- **Team Management**: Manage team rosters and team-level data
- **Training Management**: Schedule and plan training sessions with attendance tracking
- **Match Management**: Schedule matches and record results
- **Statistics Visualization**: Charts and tables for performance analysis

Each UI component is implemented as a separate module under the `ui/` directory.

### Service Layer (services/)

Services implement the business logic and provide an abstraction over the data layer:

- **AuthService**: Handles user authentication and registration
- **PlayerService**: Manages player data and operations
- **TeamService**: Manages team data and relationships
- **TrainingService**: Handles training schedules and plans
- **StatisticsService**: Calculates and presents performance metrics

### Configuration (config.py)

The Config class stores application-wide settings including:
- Application name and version
- Database connection details
- File paths for resources and media
- Logging configuration

### Database (database.py)

Database operations are abstracted through SQLAlchemy with:
- SQLite backend (file-based database)
- Session management
- Initialization/migration mechanisms

## Data Flow

1. User authenticates through the login window
2. The main window loads with tabs for different functional areas
3. When a user interacts with a UI component, the corresponding service is called
4. Services perform business logic operations and interact with the database
5. Data changes are persisted to the SQLite database
6. UI is updated to reflect the changes

## External Dependencies

The application relies on several key Python libraries:

- **PyQt5**: For the graphical user interface
- **SQLAlchemy**: For ORM and database operations
- **matplotlib**: For data visualization and charts
- **pandas/numpy**: For data processing and analysis
- **werkzeug**: For security features (password hashing)

## Deployment Strategy

The application is designed as a desktop application with a local SQLite database. It requires:

1. Python 3.11 or later
2. Installation of required Python packages (PyQt5, SQLAlchemy, matplotlib, pandas, numpy, werkzeug)
3. Appropriate system-level dependencies for graphical and multimedia operations

The deployment process is simplified in the replit environment with a pre-configured workflow that:
1. Installs the required dependencies
2. Launches the application through `main.py`

## Development Guidelines

When extending the application:

1. Maintain the existing architecture with separation between UI, services, and data layers
2. Use services for all business logic operations rather than putting logic in UI components
3. Follow the existing error handling patterns with dedicated utility functions
4. Ensure all user-facing text is in Russian to maintain language consistency
5. When adding new models, ensure they're properly registered in the initialization sequence in database.py

## Database Schema

The application uses a relational model with key tables including:
- users - for user/coach information and authentication
- teams - for team details
- players - for player information
- training - for training session schedules
- matches - for match schedules and results
- player_stats - for individual player performance metrics
- team_stats - for team-level statistics
- attendance - for tracking player attendance

All database tables are created automatically on first run via SQLAlchemy's metadata system.