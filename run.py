#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OKR Tracker - A Flask application to track Objectives and Key Results.
"""

from app import create_app
from app.models import db

app = create_app()

# Create all database tables
with app.app_context():
    db.create_all()
    print("Database tables created!")

if __name__ == '__main__':
    app.run(debug=True, port=5001)