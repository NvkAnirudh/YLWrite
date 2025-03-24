from flask import Flask
from app.ui import register_blueprints

def create_app():
    app = Flask(__name__)
    
    # Configure the app
    app.config.from_object('config.Config')
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return "Page not found", 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return "Internal server error", 500
    
    return app
