#!/usr/bin/env python3
"""
Simple script to test if the Flask application can be imported and instantiated.
This verifies that the basic structure and dependencies are correct.
"""

try:
    from app import create_app
    
    # Create the app instance
    app = create_app()
    
    # Print success message
    print("✅ Flask application loaded successfully!")
    print("The application is ready to run with: ./run.py")
    print("You can also run manually with: python run.py")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("There may be issues with the application structure or dependencies.")
    print("Check your virtual environment and installed packages.")
    
except Exception as e:
    print(f"❌ Unexpected Error: {e}")
    print("Please check your application code and dependencies.")