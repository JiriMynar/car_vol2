from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from src.models.database import db
from src.models.app_user import AppUser
from src.models.role import Role
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Mock SSO přihlašovací endpoint. V reálné implementaci by se integroval s LDAP/Active Directory.
    Pro demo účely přijímá intranet_id a vytváří/vrací JWT token.
    """
    data = request.get_json()
    
    if not data or 'intranet_id' not in data:
        return jsonify({'error': 'intranet_id je povinný'}), 400
    
    intranet_id = data['intranet_id']
    
    # Pokus o nalezení existujícího uživatele
    user = AppUser.query.filter_by(intranet_id=intranet_id).first()
    
    # Pokud uživatel neexistuje, vytvoří se mock uživatel (v reálné implementaci by přišel z LDAP)
    if not user:
        # Získání nebo vytvoření výchozí role Employee
        employee_role = Role.query.filter_by(role_name='Employee').first()
        if not employee_role:
            employee_role = Role(role_name='Employee', description='Standardní zaměstnanec se základními oprávněními pro rezervace')
            db.session.add(employee_role)
            db.session.commit()
        
        # Vytvoření mock uživatelských dat na základě intranet_id
        if intranet_id == 'admin':
            # Vytvoření admin uživatele
            admin_role = Role.query.filter_by(role_name='Fleet Administrator').first()
            if not admin_role:
                admin_role = Role(role_name='Fleet Administrator', description='Administrátor s plným přístupem ke správě vozového parku')
                db.session.add(admin_role)
                db.session.commit()
            
            user = AppUser(
                intranet_id=intranet_id,
                first_name='Admin',
                last_name='Uživatel',
                email='admin@company.com',
                role_id=admin_role.role_id
            )
        else:
            # Vytvoření běžného zaměstnance
            user = AppUser(
                intranet_id=intranet_id,
                first_name='Jan',
                last_name='Novák',
                email=f'{intranet_id}@company.com',
                role_id=employee_role.role_id
            )
        
        db.session.add(user)
        db.session.commit()
    
    # Vytvoření JWT tokenu
    access_token = create_access_token(
        identity=user.user_id,
        expires_delta=timedelta(hours=8)
    )
    
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Získání informací o aktuálním uživateli"""
    user_id = get_jwt_identity()
    user = AppUser.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'Uživatel nebyl nalezen'}), 404
    
    return jsonify(user.to_dict()), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Odhlašovací endpoint (v reálné implementaci by zneplatnil token)"""
    return jsonify({'message': 'Úspěšně odhlášen'}), 200

