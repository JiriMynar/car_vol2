from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.database import db
from src.models.app_user import AppUser
from src.models.role import Role

users_bp = Blueprint('users', __name__)

def require_admin():
    """Helper function to check if current user is admin"""
    user_id = get_jwt_identity()
    user = AppUser.query.get(user_id)
    if not user or not user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    return None

@users_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users (admin only)"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    users = AppUser.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@users_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get specific user (admin only or own profile)"""
    current_user_id = get_jwt_identity()
    current_user = AppUser.query.get(current_user_id)
    
    # Allow users to view their own profile or admin to view any profile
    if not current_user.is_admin() and current_user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    user = AppUser.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200

@users_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@jwt_required()
def update_user_role(user_id):
    """Update user role (admin only)"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    user = AppUser.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'role_id' not in data:
        return jsonify({'error': 'role_id is required'}), 400
    
    # Verify role exists
    role = Role.query.get(data['role_id'])
    if not role:
        return jsonify({'error': 'Role not found'}), 404
    
    user.role_id = data['role_id']
    db.session.commit()
    
    return jsonify(user.to_dict()), 200

@users_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@jwt_required()
def update_user_status(user_id):
    """Update user active status (admin only)"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    user = AppUser.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'is_active' not in data:
        return jsonify({'error': 'is_active is required'}), 400
    
    user.is_active = bool(data['is_active'])
    db.session.commit()
    
    return jsonify(user.to_dict()), 200

@users_bp.route('/roles', methods=['GET'])
@jwt_required()
def get_roles():
    """Get all roles"""
    roles = Role.query.all()
    return jsonify([role.to_dict() for role in roles]), 200

@users_bp.route('/roles', methods=['POST'])
@jwt_required()
def create_role():
    """Create new role (admin only)"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    data = request.get_json()
    
    if 'role_name' not in data:
        return jsonify({'error': 'role_name is required'}), 400
    
    # Check if role already exists
    existing_role = Role.query.filter_by(role_name=data['role_name']).first()
    if existing_role:
        return jsonify({'error': 'Role with this name already exists'}), 400
    
    role = Role(
        role_name=data['role_name'],
        description=data.get('description')
    )
    
    db.session.add(role)
    db.session.commit()
    
    return jsonify(role.to_dict()), 201

