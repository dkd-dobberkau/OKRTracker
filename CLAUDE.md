# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based OKR (Objectives and Key Results) tracking application. The application allows users to:
- Create and manage objectives
- Add key results to objectives
- Track progress on key results
- View dashboards showing overall progress

## Architecture

The application follows a typical Flask project structure:

- **Main Application**: `run.py` is the entry point for starting the application
- **Flask App Factory**: Located in `app/__init__.py` creates and configures the Flask application
- **Configuration**: `app/config.py` contains application configuration settings
- **Forms**: `app/forms.py` contains Flask-WTF form definitions
- **Database Models**: `app/models.py` contains SQLAlchemy models for User, Objective, KeyResult, and KeyResultUpdate
- **Routing**: Blueprint-based routing in the `app/routes/` directory for authentication, objectives, key results, and main pages
- **Frontend**: Uses Bootstrap 5 for styling, with custom CSS and JavaScript in the `app/static/` directory
- **Templates**: HTML templates in the `app/templates/` directory

## Database Schema

- **User**: Stores user accounts with authentication information
- **Objective**: Represents OKRs, belongs to a user
- **KeyResult**: Measurable outcomes for objectives, with target and current values
- **KeyResultUpdate**: History of updates to key result progress

## Commands

To set up the project:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

Before running the application, you may want to set environment variables:
```bash
# Set environment variables (optional)
export SECRET_KEY="your-secret-key"
export DATABASE_URL="sqlite:///okr.db"  # or your database URL
```

## Development Notes

1. The application is structured following Flask best practices, using blueprints for route organization.

2. Current directory structure:
   - app/ (main application package)
     - __init__.py (application factory)
     - config.py (configuration settings)
     - forms.py (form definitions)
     - models.py (database models)
     - routes/ (blueprint routes)
       - auth.py (authentication routes)
       - objectives.py (objective routes)
       - keyresults.py (key results routes)
       - main.py (main routes)
     - static/ (static assets)
     - templates/ (HTML templates)
   - run.py (application entry point)
   - requirements.txt (dependencies)

3. When adding new features, follow the blueprint pattern for organizing routes.

4. The application uses Flask-Login for user authentication and Flask-SQLAlchemy for database operations.