import eventlet
eventlet.monkey_patch()  # ⚠️ Precisa ser chamado antes de qualquer outro import

import os
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO


socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)


    allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
    CORS(app, resources={r"/*": {"origins": allowed_origins}})

    app.config["SECRET_KEY"] = "your_secret_key"


    socketio.init_app(app, cors_allowed_origins="*")

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
