from app import create_app, socketio
from flask_cors import CORS
import os


app = create_app()

origins = [
    "https://syncwave-x.vercel.app/",
    "http://localhost:3000",
]

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)
