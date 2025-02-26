from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
from .. import db
from ..models import User
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Registra um novo usuário.
    Espera JSON com: nome, email, usuario e senha.
    """
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    usuario = data.get('usuario')
    senha = data.get('senha')
    
    if not all([nome, email, usuario, senha]):
        return jsonify({'msg': 'Dados incompletos.'}), 400

    if User.query.filter(or_(User.email == email, User.usuario == usuario)).first():
        return jsonify({'msg': 'Usuário ou email já existente.'}), 400
    
    senha_hash = generate_password_hash(senha)
    new_user = User(nome=nome, email=email, usuario=usuario, senha_hash=senha_hash)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'msg': 'Usuário registrado com sucesso.'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Realiza o login do usuário.
    Espera JSON com: usuario e senha.
    Retorna token JWT caso as credenciais estejam corretas.
    """
    data = request.get_json()
    usuario = data.get('usuario')
    senha = data.get('senha')
    
    if not all([usuario, senha]):
        return jsonify({'msg': 'Dados incompletos.'}), 400
        
    user = User.query.filter_by(usuario=usuario).first()
    if user and check_password_hash(user.senha_hash, senha):
        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token, 'user': user.to_dict()}), 200
    else:
        return jsonify({'msg': 'Credenciais inválidas.'}), 401
