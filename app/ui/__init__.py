from app.ui.views import ui_bp

def register_blueprints(app):
    app.register_blueprint(ui_bp, url_prefix='/')
