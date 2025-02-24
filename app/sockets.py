from flask import request
from flask_socketio import join_room, leave_room, emit
from flask_jwt_extended import decode_token
from .models import Room
from . import db

room_participants = {}

def register_socket_handlers(socketio):
    @socketio.on('connect')
    def handle_connect():
        """
        Durante a conexão, espera-se que o token JWT seja enviado
        via query string para autenticar o usuário.
        """
        token = request.args.get('token')
        if not token:
            return False 
        try:
            decoded = decode_token(token)
            user_id = decoded['sub']
            request.environ['user_id'] = user_id
        except Exception:
            return False  

    @socketio.on('join_room')
    def handle_join(data):
        """
        Evento para entrada em sala via WebSocket.
        Dados esperados: { "room_id": <ID_da_Sala> }
        """
        user_id = request.environ.get('user_id')
        room_id = data.get('room_id')
        if not user_id or not room_id:
            emit('error', {'msg': 'Dados insuficientes para entrar na sala.'})
            return
        join_room(str(room_id))

        # Atualiza a lista de participantes da sala
        participants = room_participants.get(str(room_id), set())
        participants.add(user_id)
        room_participants[str(room_id)] = participants

        # Emite evento com a lista atualizada de participantes
        emit('participants_update', {'participants': list(participants)}, room=str(room_id))
    
    @socketio.on('leave_room')
    def handle_leave(data):
        """
        Evento para saída da sala.
        Dados esperados: { "room_id": <ID_da_Sala> }
        """
        user_id = request.environ.get('user_id')
        room_id = data.get('room_id')
        if not user_id or not room_id:
            emit('error', {'msg': 'Dados insuficientes para sair da sala.'})
            return
        leave_room(str(room_id))

        # Atualiza a lista de participantes da sala
        participants = room_participants.get(str(room_id), set())
        participants.discard(user_id)
        room_participants[str(room_id)] = participants

        # Emite evento com a lista atualizada de participantes
        emit('participants_update', {'participants': list(participants)}, room=str(room_id))
    
    @socketio.on('play_video')
    def handle_play(data):
        """
        Evento para iniciar o vídeo.
        Apenas o host pode emitir este comando e o vídeo só inicia se houver
        pelo menos 2 participantes na sala.
        Dados esperados: { "room_id": <ID_da_Sala> }
        """
        user_id = request.environ.get('user_id')
        room_id = data.get('room_id')
        if not user_id or not room_id:
            emit('error', {'msg': 'Dados insuficientes.'})
            return
        
        room = Room.query.get(room_id)
        if not room:
            emit('error', {'msg': 'Sala não encontrada.'})
            return
        
        if room.host_id != user_id:
            emit('error', {'msg': 'Apenas o host pode controlar o vídeo.'})
            return
        
        participants = room_participants.get(str(room_id), set())
        if len(participants) < 2:
            emit('error', {'msg': 'É necessário pelo menos 2 participantes para iniciar o vídeo.'})
            return
        
        emit('play_video', {'msg': 'Vídeo iniciado.'}, room=str(room_id))
    
    @socketio.on('pause_video')
    def handle_pause(data):
        """
        Evento para pausar o vídeo.
        Apenas o host pode pausar o vídeo.
        Dados esperados: { "room_id": <ID_da_Sala> }
        """
        user_id = request.environ.get('user_id')
        room_id = data.get('room_id')
        if not user_id or not room_id:
            emit('error', {'msg': 'Dados insuficientes.'})
            return
        
        room = Room.query.get(room_id)
        if not room:
            emit('error', {'msg': 'Sala não encontrada.'})
            return
        
        if room.host_id != user_id:
            emit('error', {'msg': 'Apenas o host pode controlar o vídeo.'})
            return
        
        emit('pause_video', {'msg': 'Vídeo pausado.'}, room=str(room_id))
    
    @socketio.on('chat_message')
    def handle_chat_message(data):
        """
        Permite o envio de mensagens de chat em tempo real.
        Dados esperados: { "room_id": <ID_da_Sala>, "mensagem": "texto da mensagem" }
        """
        user_id = request.environ.get('user_id')
        room_id = data.get('room_id')
        mensagem = data.get('mensagem')
        if not user_id or not room_id or not mensagem:
            emit('error', {'msg': 'Dados insuficientes para enviar mensagem.'})
            return
        
        emit('chat_message', {'user_id': user_id, 'mensagem': mensagem}, room=str(room_id))
