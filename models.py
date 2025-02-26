from . import db
from datetime import datetime

class User(db.Model):
    """Modelo do usuário."""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    

    rooms = db.relationship('Room', backref='host', lazy=True)

    room_participations = db.relationship(
        'RoomParticipant', backref='user', lazy=True, cascade="all, delete-orphan"
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'usuario': self.usuario
        }

class Room(db.Model):
    """Modelo de sala de transmissão."""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    is_public = db.Column(db.Boolean, default=True)
    senha_hash = db.Column(db.String(128), nullable=True)
    host_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    participants = db.relationship(
        'RoomParticipant', backref='room', lazy=True, cascade="all, delete-orphan"
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'is_public': self.is_public,
            'host_id': self.host_id,
            'created_at': self.created_at.isoformat()
        }

class RoomParticipant(db.Model):
    """Associação entre usuários e salas."""
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
