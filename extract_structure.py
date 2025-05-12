#!/usr/bin/env python3
"""
Script to extract the commented structure in flask-okr-app.py to actual files.
This will create the proper directory structure for the Flask OKR application.
"""

import os
import re
from pathlib import Path

def ensure_dir(directory):
    """Create directory if it doesn't exist"""
    Path(directory).mkdir(parents=True, exist_ok=True)

def extract_section(content, section_name):
    """Extract a section from the content"""
    pattern = fr"# {section_name}\n\"\"\"(.*?)\"\"\""
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def main():
    # Read the source file
    with open('flask-okr-app.py', 'r') as f:
        content = f.read()
    
    # Create necessary directories
    ensure_dir('routes')
    ensure_dir('templates/auth')
    ensure_dir('templates/objectives')
    ensure_dir('templates/keyresults')
    ensure_dir('templates/errors')
    ensure_dir('static/css')
    ensure_dir('static/js')
    
    # Extract and write config.py
    config_content = extract_section(content, "config.py")
    if config_content:
        with open('config.py', 'w') as f:
            f.write(config_content)
    
    # Extract and write models.py
    models_content = extract_section(content, "models.py")
    if models_content:
        with open('models.py', 'w') as f:
            f.write(models_content)
    
    # Extract and write routes
    routes = {
        "routes/auth.py": extract_section(content, "routes/auth.py"),
        "routes/objectives.py": extract_section(content, "routes/objectives.py"),
        "routes/keyresults.py": extract_section(content, "routes/keyresults.py"),
        "routes/main.py": extract_section(content, "routes/main.py")
    }
    
    for route_file, route_content in routes.items():
        if route_content:
            with open(route_file, 'w') as f:
                f.write(route_content)
    
    # Extract and write forms.py
    forms_content = extract_section(content, "forms.py")
    if forms_content:
        with open('forms.py', 'w') as f:
            f.write(forms_content)
    
    # Extract and write app.py
    app_content = extract_section(content, "app.py \(Main application file\)")
    if app_content:
        with open('app.py', 'w') as f:
            f.write(app_content)
    
    # Extract and write templates
    templates = {
        "templates/base.html": extract_section(content, "templates/base.html"),
        "templates/dashboard.html": extract_section(content, "templates/dashboard.html"),
        "templates/objectives/view.html": extract_section(content, "templates/objectives/view.html")
    }
    
    for template_file, template_content in templates.items():
        if template_content:
            with open(template_file, 'w') as f:
                f.write(template_content)
    
    # Extract and write static files
    static_files = {
        "static/css/style.css": extract_section(content, "static/css/style.css"),
        "static/js/main.js": extract_section(content, "static/js/main.js")
    }
    
    for static_file, static_content in static_files.items():
        if static_content:
            with open(static_file, 'w') as f:
                f.write(static_content)

    print("Structure extracted successfully!")

if __name__ == "__main__":
    main()