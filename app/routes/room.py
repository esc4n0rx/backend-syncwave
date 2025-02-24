from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db, socketio
from ..models import Room, RoomParticipant, User

room_bp = Blueprint('room', __name__)

def get_room_details(room):
    """
    Retorna um dicionário com os detalhes da sala,
    incluindo as informações do host e a lista de participantes.
    """
    host = User.query.get(room.host_id)
    participants = RoomParticipant.query.filter_by(room_id=room.id).all()
    participant_list = []
    for participant in participants:
        user = User.query.get(participant.user_id)
        if user:
            participant_list.append({
                'id': user.id,
                'nome': user.nome,
                'usuario': user.usuario
            })
    room_dict = room.to_dict()  # Certifique-se de que Room.to_dict() retorna pelo menos id, nome, is_public, host_id e created_at
    room_dict['host'] = {
        'id': host.id,
        'nome': host.nome,
        'usuario': host.usuario
    } if host else None
    room_dict['participants'] = participant_list
    return room_dict

@room_bp.route('/', methods=['POST'])
@jwt_required()
def create_room():
    """
    Cria uma nova sala.
    Espera JSON com:
      - nome: nome da sala
      - is_public: booleano informando se a sala é pública (default True)
      - senha: (opcional) senha para salas privadas
    Apenas o usuário autenticado (host) poderá criar a sala.
    """
    data = request.get_json()
    nome = data.get('nome')
    is_public = data.get('is_public', True)
    senha = data.get('senha') 

    if not nome:
        return jsonify({'msg': 'Nome da sala é obrigatório.'}), 400

    host_id = get_jwt_identity()
    senha_hash = generate_password_hash(senha) if (not is_public and senha) else None

    new_room = Room(nome=nome, is_public=is_public, senha_hash=senha_hash, host_id=host_id)
    db.session.add(new_room)
    db.session.commit()

    # Associa o host à sala
    host_association = RoomParticipant(room_id=new_room.id, user_id=host_id)
    db.session.add(host_association)
    db.session.commit()

    return jsonify({'msg': 'Sala criada com sucesso.', 'room': get_room_details(new_room)}), 201

@room_bp.route('/join', methods=['POST'])
@jwt_required()
def join_room():
    """
    Permite a entrada em uma sala.
    Espera JSON com:
      - room_id: ID da sala
      - senha: (se a sala for privada)
    """
    data = request.get_json()
    room_id = data.get('room_id')
    senha = data.get('senha')

    if not room_id:
        return jsonify({'msg': 'ID da sala é obrigatório.'}), 400

    room = Room.query.get(room_id)
    if not room:
        return jsonify({'msg': 'Sala não encontrada.'}), 404

    if not room.is_public:
        if not senha or not check_password_hash(room.senha_hash, senha):
            return jsonify({'msg': 'Senha incorreta para sala privada.'}), 403

    user_id = get_jwt_identity()

    existing_participation = RoomParticipant.query.filter_by(room_id=room_id, user_id=user_id).first()
    if existing_participation:
        return jsonify({'msg': 'Usuário já associado à sala.', 'room': get_room_details(room)}), 200

    new_participation = RoomParticipant(room_id=room_id, user_id=user_id)
    db.session.add(new_participation)
    db.session.commit()

    return jsonify({'msg': 'Entrada na sala autorizada.', 'room': get_room_details(room)}), 200

@room_bp.route('/<int:room_id>', methods=['DELETE'])
@jwt_required()
def delete_room(room_id):
    """
    Exclui uma sala.
    Apenas o host (criador da sala) pode apagar a sala.
    Antes de excluir, os usuários conectados são notificados via SocketIO.
    """
    user_id = get_jwt_identity()
    room = Room.query.get(room_id)

    if not room:
        return jsonify({'msg': 'Sala não encontrada.'}), 404

    if room.host_id != user_id:
        return jsonify({'msg': 'Apenas o host pode excluir a sala.'}), 403

    socketio.emit('room_deleted', {'msg': 'A sala foi apagada pelo host.'}, room=str(room_id))

    RoomParticipant.query.filter_by(room_id=room_id).delete()

    db.session.delete(room)
    db.session.commit()

    return jsonify({'msg': 'Sala deletada com sucesso.'}), 200

@room_bp.route('/', methods=['GET'])
@jwt_required()
def list_rooms():
    """
    Lista todas as salas com detalhes, incluindo:
      - Dados da sala (id, nome, is_public, host, data de criação)
      - Lista de participantes
    """
    rooms = Room.query.all()
    room_list = [get_room_details(room) for room in rooms]
    return jsonify({'rooms': room_list}), 200
