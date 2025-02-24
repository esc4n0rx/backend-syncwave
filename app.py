import eventlet
eventlet.monkey_patch()  

import os
from flask import Flask
from flask_cors import CORS
from app import create_app, socketio


app = create_app()


allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
CORS(app, resources={r"/*": {"origins": allowed_origins}})


with app.app_context():
    if __name__ == '__main__':
        port = int(os.environ.get("PORT", 5000))
        socketio.run(app, host='0.0.0.0', port=port)


