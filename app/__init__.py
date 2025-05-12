from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from app.config import Config
from app.models import db, User
from datetime import datetime

# Import blueprints
from app.routes.auth import auth_bp
from app.routes.objectives import objectives_bp
from app.routes.keyresults import keyresults_bp
from app.routes.main import main_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Setup login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(objectives_bp)
    app.register_blueprint(keyresults_bp)
    app.register_blueprint(main_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Add current year to all templates
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Create all database tables
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)