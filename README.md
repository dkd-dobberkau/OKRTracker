# OKR Tracker

A Flask-based web application for tracking Objectives and Key Results (OKRs).

## Features

- User authentication system with registration and login
- Create, view, edit, and delete objectives
- Add key results to objectives with target and current values
- Track progress visually with progress bars
- Dashboard with overall progress visualization
- Responsive design using Bootstrap 5

## Tech Stack

- **Backend**: Flask 3.1.0, Python 3.12
- **Database**: SQLAlchemy with SQLite
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF
- **Frontend**: Bootstrap 5, JavaScript
- **Database Migrations**: Flask-Migrate

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd OKR
```

2. Create a Python 3.12 virtual environment:

```bash
python3.12 -m venv venv
```

3. Activate the virtual environment:

```bash
# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

4. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The application uses environment variables for configuration. You can set these in a `.env` file in the root directory:

```
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///okr.db
```

## Running the Application

To run the application:

```bash
python run.py
```

The application will be available at http://127.0.0.1:5001

## Project Structure

```
.
├── app/                    # Application package
│   ├── __init__.py         # App initialization
│   ├── config.py           # Configuration settings
│   ├── forms.py            # Form definitions
│   ├── models.py           # Database models
│   ├── routes/             # Blueprint routes
│   │   ├── auth.py         # Authentication routes
│   │   ├── keyresults.py   # Key results routes
│   │   ├── main.py         # Main routes
│   │   └── objectives.py   # Objective routes
│   ├── static/             # Static files
│   │   ├── css/            # CSS files
│   │   └── js/             # JavaScript files
│   └── templates/          # HTML templates
├── instance/               # Instance-specific files
│   └── okr.db              # SQLite database
├── venv/                   # Virtual environment
├── .env                    # Environment variables
├── .gitignore              # Git ignore file
├── CLAUDE.md               # Claude Code guidance
├── README.md               # This file
├── requirements.txt        # Dependencies
└── run.py                  # Application entry point
```

## Usage Guide

1. **Register and Login**: Create a new account and login to access the dashboard
2. **Create Objectives**: Add new objectives with title, description, and time frame
3. **Add Key Results**: Add measurable key results to objectives
4. **Track Progress**: Update the current value of key results to track progress
5. **View Dashboard**: See overall progress and upcoming objectives on the dashboard

## Development

### Creating the Database

The database tables are automatically created when the application starts. If you need to recreate the database, you can delete the `instance/okr.db` file and restart the application.

### Running in Debug Mode

The application runs in debug mode by default, which enables auto-reload on code changes.

## License

MIT