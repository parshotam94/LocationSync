from flask import Flask
from .config import Config
from .extensions import mysql, socketio

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    mysql.init_app(app)
    socketio.init_app(app)

    # Register Blueprints
    from .routes.group_routes import group_bp
    from .routes.auth_routes import auth_bp

    app.register_blueprint(group_bp)
    app.register_blueprint(auth_bp)

    # Register socket events
    from .sockets.events import register_socket_events
    register_socket_events(socketio)

    return app