from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.database import db
from src.models.service_record import ServiceRecord
from src.models.vehicle import Vehicle
from src.models.app_user import AppUser
from datetime import datetime

service_records_bp = Blueprint('service_records', __name__)

def require_admin():
    """Helper function to check if current user is admin"""
    user_id = get_jwt_identity()
    user = AppUser.query.get(user_id)
    if not user or not user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    return None

@service_records_bp.route('/service-records', methods=['GET'])
@jwt_required()
def get_service_records():
    """Get service records with optional filtering"""
    vehicle_id = request.args.get('vehicle_id')
    
    query = ServiceRecord.query
    
    if vehicle_id:
        query = query.filter_by(vehicle_id=int(vehicle_id))
    
    service_records = query.order_by(ServiceRecord.service_date.desc()).all()
    return jsonify([record.to_dict() for record in service_records]), 200

@service_records_bp.route('/service-records/<int:service_id>', methods=['GET'])
@jwt_required()
def get_service_record(service_id):
    """Get specific service record"""
    service_record = ServiceRecord.query.get_or_404(service_id)
    return jsonify(service_record.to_dict()), 200

@service_records_bp.route('/service-records', methods=['POST'])
@jwt_required()
def create_service_record():
    """Create new service record (admin only)"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['vehicle_id', 'service_date', 'service_type', 'description']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Verify vehicle exists
    vehicle = Vehicle.query.get(data['vehicle_id'])
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
    
    try:
        # Parse service date
        service_date = datetime.strptime(data['service_date'], '%Y-%m-%d').date()
        
        service_record = ServiceRecord(
            vehicle_id=data['vehicle_id'],
            service_date=service_date,
            service_type=data['service_type'],
            description=data['description'],
            cost=float(data['cost']) if data.get('cost') else None,
            performed_by=data.get('performed_by')
        )
        
        db.session.add(service_record)
        
        # Update vehicle's last service date if this is more recent
        if not vehicle.last_service_date or service_date > vehicle.last_service_date:
            vehicle.last_service_date = service_date
        
        db.session.commit()
        
        return jsonify(service_record.to_dict()), 201
        
    except ValueError:
        return jsonify({'error': 'Invalid date format for service_date. Use YYYY-MM-DD'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@service_records_bp.route('/service-records/<int:service_id>', methods=['PUT'])
@jwt_required()
def update_service_record(service_id):
    """Update service record (admin only)"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    service_record = ServiceRecord.query.get_or_404(service_id)
    data = request.get_json()
    
    try:
        # Update fields
        updatable_fields = ['service_type', 'description', 'performed_by']
        for field in updatable_fields:
            if field in data:
                setattr(service_record, field, data[field])
        
        if 'service_date' in data:
            service_record.service_date = datetime.strptime(data['service_date'], '%Y-%m-%d').date()
        
        if 'cost' in data:
            service_record.cost = float(data['cost']) if data['cost'] else None
        
        db.session.commit()
        return jsonify(service_record.to_dict()), 200
        
    except ValueError:
        return jsonify({'error': 'Invalid date format for service_date. Use YYYY-MM-DD'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@service_records_bp.route('/service-records/<int:service_id>', methods=['DELETE'])
@jwt_required()
def delete_service_record(service_id):
    """Delete service record (admin only)"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    service_record = ServiceRecord.query.get_or_404(service_id)
    db.session.delete(service_record)
    db.session.commit()
    
    return jsonify({'message': 'Service record deleted successfully'}), 200

@service_records_bp.route('/vehicles/<int:vehicle_id>/service-records', methods=['GET'])
@jwt_required()
def get_vehicle_service_records(vehicle_id):
    """Get all service records for a specific vehicle"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    service_records = ServiceRecord.query.filter_by(vehicle_id=vehicle_id).order_by(ServiceRecord.service_date.desc()).all()
    return jsonify([record.to_dict() for record in service_records]), 200

