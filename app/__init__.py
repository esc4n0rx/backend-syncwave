from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from .config import Config

# Instâncias globais
db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins="*", async_mode='eventlet')

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app)

    with app.app_context():
        from . import models
        db.create_all()

    from .routes.auth import auth_bp
    from .routes.room import room_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(room_bp, url_prefix='/api/rooms')

    from .sockets import register_socket_handlers
    register_socket_handlers(socketio)

    return app
