import eventlet
eventlet.monkey_patch()  

import os
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from routes.auth import auth_bp
from routes.room import room_bp


socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)


    CORS(app, resources={r"/*": {"origins": "*"}})

    app.config["SECRET_KEY"] = "your_secret_key"

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(room_bp, url_prefix='/api/rooms')

    socketio.init_app(app, cors_allowed_origins="*")

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
