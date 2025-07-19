from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.database import db
from src.models.vehicle import Vehicle
from src.models.app_user import AppUser
from datetime import datetime, date

vehicles_bp = Blueprint('vehicles', __name__)

def require_admin():
    """Helper function to check if current user is admin"""
    user_id = get_jwt_identity()
    user = AppUser.query.get(user_id)
    if not user or not user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    return None

@vehicles_bp.route('/vehicles', methods=['GET'])
@jwt_required()
def get_vehicles():
    """Get all vehicles with optional filtering"""
    status = request.args.get('status', 'Active')
    
    query = Vehicle.query
    if status and status != 'all':
        query = query.filter_by(status=status)
    
    vehicles = query.all()
    return jsonify([vehicle.to_dict() for vehicle in vehicles]), 200

@vehicles_bp.route('/vehicles/<int:vehicle_id>', methods=['GET'])
@jwt_required()
def get_vehicle(vehicle_id):
    """Get specific vehicle by ID"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    return jsonify(vehicle.to_dict()), 200

@vehicles_bp.route('/vehicles', methods=['POST'])
@jwt_required()
def create_vehicle():
    """Create new vehicle (admin only)"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['make', 'model', 'license_plate', 'fuel_type', 'seating_capacity', 'transmission_type']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check if license plate already exists
    existing_vehicle = Vehicle.query.filter_by(license_plate=data['license_plate']).first()
    if existing_vehicle:
        return jsonify({'error': 'Vehicle with this license plate already exists'}), 400
    
    try:
        vehicle = Vehicle(
            make=data['make'],
            model=data['model'],
            license_plate=data['license_plate'],
            color=data.get('color'),
            fuel_type=data['fuel_type'],
            seating_capacity=int(data['seating_capacity']),
            transmission_type=data['transmission_type'],
            status=data.get('status', 'Active'),
            description=data.get('description'),
            odometer_reading=int(data.get('odometer_reading', 0)),
            entry_permissions_notes=data.get('entry_permissions_notes')
        )
        
        # Handle date fields
        date_fields = [
            'last_service_date', 'next_service_date', 'technical_inspection_expiry_date',
            'highway_vignette_expiry_date', 'emission_inspection_expiry_date'
        ]
        
        for field in date_fields:
            if data.get(field):
                try:
                    setattr(vehicle, field, datetime.strptime(data[field], '%Y-%m-%d').date())
                except ValueError:
                    return jsonify({'error': f'Invalid date format for {field}. Use YYYY-MM-DD'}), 400
        
        db.session.add(vehicle)
        db.session.commit()
        
        return jsonify(vehicle.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@vehicles_bp.route('/vehicles/<int:vehicle_id>', methods=['PUT'])
@jwt_required()
def update_vehicle(vehicle_id):
    """Update vehicle (admin only)"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    data = request.get_json()
    
    try:
        # Update basic fields
        updatable_fields = [
            'make', 'model', 'license_plate', 'color', 'fuel_type', 
            'seating_capacity', 'transmission_type', 'status', 'description',
            'odometer_reading', 'entry_permissions_notes'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field in ['seating_capacity', 'odometer_reading']:
                    setattr(vehicle, field, int(data[field]))
                else:
                    setattr(vehicle, field, data[field])
        
        # Handle date fields
        date_fields = [
            'last_service_date', 'next_service_date', 'technical_inspection_expiry_date',
            'highway_vignette_expiry_date', 'emission_inspection_expiry_date'
        ]
        
        for field in date_fields:
            if field in data:
                if data[field]:
                    try:
                        setattr(vehicle, field, datetime.strptime(data[field], '%Y-%m-%d').date())
                    except ValueError:
                        return jsonify({'error': f'Invalid date format for {field}. Use YYYY-MM-DD'}), 400
                else:
                    setattr(vehicle, field, None)
        
        db.session.commit()
        return jsonify(vehicle.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@vehicles_bp.route('/vehicles/<int:vehicle_id>', methods=['DELETE'])
@jwt_required()
def delete_vehicle(vehicle_id):
    """Delete/Archive vehicle (admin only)"""
    admin_check = require_admin()
    if admin_check:
        return admin_check
    
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Instead of deleting, archive the vehicle
    vehicle.status = 'Archived'
    db.session.commit()
    
    return jsonify({'message': 'Vehicle archived successfully'}), 200

@vehicles_bp.route('/vehicles/<int:vehicle_id>/availability', methods=['GET'])
@jwt_required()
def check_vehicle_availability(vehicle_id):
    """Check vehicle availability for given time period"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    start_time_str = request.args.get('start_time')
    end_time_str = request.args.get('end_time')
    
    if not start_time_str or not end_time_str:
        return jsonify({'error': 'start_time and end_time parameters are required'}), 400
    
    try:
        start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
    except ValueError:
        return jsonify({'error': 'Invalid datetime format. Use ISO format'}), 400
    
    is_available = vehicle.is_available(start_time, end_time)
    
    return jsonify({
        'vehicle_id': vehicle_id,
        'available': is_available,
        'start_time': start_time_str,
        'end_time': end_time_str
    }), 200

