from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.database import db
from src.models.damage_record import DamageRecord
from src.models.vehicle import Vehicle
from src.models.app_user import AppUser
from datetime import datetime

damage_records_bp = Blueprint('damage_records', __name__)

def require_admin():
    """Helper function to check if current user is admin"""
    user_id = get_jwt_identity()
    user = AppUser.query.get(user_id)
    if not user or not user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    return None

@damage_records_bp.route('/damage-records', methods=['GET'])
@jwt_required()
def get_damage_records():
    """Get damage records with optional filtering"""
    vehicle_id = request.args.get('vehicle_id')
    repair_status = request.args.get('repair_status')
    
    query = DamageRecord.query
    
    if vehicle_id:
        query = query.filter_by(vehicle_id=int(vehicle_id))
    
    if repair_status:
        query = query.filter_by(repair_status=repair_status)
    
    damage_records = query.order_by(DamageRecord.date_of_damage.desc()).all()
    return jsonify([record.to_dict() for record in damage_records]), 200

@damage_records_bp.route('/damage-records/<int:damage_id>', methods=['GET'])
@jwt_required()
def get_damage_record(damage_id):
    """Get specific damage record"""
    damage_record = DamageRecord.query.get_or_404(damage_id)
    return jsonify(damage_record.to_dict()), 200

@damage_records_bp.route('/damage-records', methods=['POST'])
@jwt_required()
def create_damage_record():
    """Create new damage record (admin only)"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['vehicle_id', 'date_of_damage', 'description']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Verify vehicle exists
    vehicle = Vehicle.query.get(data['vehicle_id'])
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    try:
        # Parse damage date
        damage_date = datetime.strptime(data['date_of_damage'], '%Y-%m-%d').date()
        
        damage_record = DamageRecord(
            vehicle_id=data['vehicle_id'],
            date_of_damage=damage_date,
            description=data['description'],
            estimated_cost=float(data['estimated_cost']) if data.get('estimated_cost') else None,
            actual_cost=float(data['actual_cost']) if data.get('actual_cost') else None,
            repair_status=data.get('repair_status', 'Pending')
        )
        
        # Handle photos if provided
        if data.get('photos') and isinstance(data['photos'], list):
            import json
            damage_record.photos = json.dumps(data['photos'])
        
        db.session.add(damage_record)
        db.session.commit()
        
        return jsonify(damage_record.to_dict()), 201
        
    except ValueError:
        return jsonify({'error': 'Invalid date format for date_of_damage. Use YYYY-MM-DD'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@damage_records_bp.route('/damage-records/<int:damage_id>', methods=['PUT'])
@jwt_required()
def update_damage_record(damage_id):
    """Update damage record (admin only)"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    damage_record = DamageRecord.query.get_or_404(damage_id)
    data = request.get_json()
    
    try:
        # Update fields
        updatable_fields = ['description', 'repair_status']
        for field in updatable_fields:
            if field in data:
                setattr(damage_record, field, data[field])
        
        if 'date_of_damage' in data:
            damage_record.date_of_damage = datetime.strptime(data['date_of_damage'], '%Y-%m-%d').date()
        
        if 'estimated_cost' in data:
            damage_record.estimated_cost = float(data['estimated_cost']) if data['estimated_cost'] else None
        
        if 'actual_cost' in data:
            damage_record.actual_cost = float(data['actual_cost']) if data['actual_cost'] else None
        
        # Handle photos update
        if 'photos' in data:
            if data['photos'] and isinstance(data['photos'], list):
                import json
                damage_record.photos = json.dumps(data['photos'])
            else:
                damage_record.photos = None
        
        db.session.commit()
        return jsonify(damage_record.to_dict()), 200
        
    except ValueError:
        return jsonify({'error': 'Invalid date format for date_of_damage. Use YYYY-MM-DD'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@damage_records_bp.route('/damage-records/<int:damage_id>', methods=['DELETE'])
@jwt_required()
def delete_damage_record(damage_id):
    """Delete damage record (admin only)"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    damage_record = DamageRecord.query.get_or_404(damage_id)
    db.session.delete(damage_record)
    db.session.commit()
    
    return jsonify({'message': 'Damage record deleted successfully'}), 200

@damage_records_bp.route('/vehicles/<int:vehicle_id>/damage-records', methods=['GET'])
@jwt_required()
def get_vehicle_damage_records(vehicle_id):
    """Get all damage records for a specific vehicle"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    damage_records = DamageRecord.query.filter_by(vehicle_id=vehicle_id).order_by(DamageRecord.date_of_damage.desc()).all()
    return jsonify([record.to_dict() for record in damage_records]), 200

