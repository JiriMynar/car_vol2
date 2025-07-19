from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.database import db
from src.models.reservation import Reservation
from src.models.vehicle import Vehicle
from src.models.app_user import AppUser
from datetime import datetime

reservations_bp = Blueprint('reservations', __name__)

@reservations_bp.route('/reservations', methods=['GET'])
@jwt_required()
def get_reservations():
    """Get reservations (all for admin, own for regular users)"""
    user_id = get_jwt_identity()
    user = AppUser.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    query = Reservation.query
    
    # If not admin, only show user's own reservations
    if not user.is_admin():
        query = query.filter_by(user_id=user_id)
    
    # Optional filtering
    vehicle_id = request.args.get('vehicle_id')
    status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if vehicle_id:
        query = query.filter_by(vehicle_id=int(vehicle_id))
    
    if status:
        query = query.filter_by(status=status)
    
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Reservation.start_time >= start_dt)
        except ValueError:
            return jsonify({'error': 'Invalid start_date format. Use YYYY-MM-DD'}), 400
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(Reservation.end_time <= end_dt)
        except ValueError:
            return jsonify({'error': 'Invalid end_date format. Use YYYY-MM-DD'}), 400
    
    reservations = query.order_by(Reservation.start_time.desc()).all()
    return jsonify([reservation.to_dict() for reservation in reservations]), 200

@reservations_bp.route('/reservations/<int:reservation_id>', methods=['GET'])
@jwt_required()
def get_reservation(reservation_id):
    """Get specific reservation"""
    user_id = get_jwt_identity()
    user = AppUser.query.get(user_id)
    
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Check if user can access this reservation
    if not user.is_admin() and reservation.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(reservation.to_dict()), 200

@reservations_bp.route('/reservations', methods=['POST'])
@jwt_required()
def create_reservation():
    """Create new reservation"""
    user_id = get_jwt_identity()
    user = AppUser.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['vehicle_id', 'start_time', 'end_time', 'purpose', 'destination']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    try:
        # Parse datetime strings
        start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
        
        # Validate time range
        if start_time >= end_time:
            return jsonify({'error': 'End time must be after start time'}), 400
        
        if start_time < datetime.utcnow():
            return jsonify({'error': 'Cannot create reservation in the past'}), 400
        
        # Check vehicle exists and is available
        vehicle = Vehicle.query.get(data['vehicle_id'])
        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404
        
        if not vehicle.is_available(start_time, end_time):
            return jsonify({'error': 'Vehicle is not available for the selected time period'}), 400
        
        # Create reservation (admin can create for other users)
        target_user_id = user_id
        if user.is_admin() and 'user_id' in data:
            target_user_id = data['user_id']
            # Verify target user exists
            target_user = AppUser.query.get(target_user_id)
            if not target_user:
                return jsonify({'error': 'Target user not found'}), 404
        
        reservation = Reservation(
            vehicle_id=data['vehicle_id'],
            user_id=target_user_id,
            start_time=start_time,
            end_time=end_time,
            purpose=data['purpose'],
            destination=data['destination'],
            number_of_passengers=data.get('number_of_passengers'),
            user_notes=data.get('user_notes'),
            admin_notes=data.get('admin_notes') if user.is_admin() else None
        )
        
        db.session.add(reservation)
        db.session.commit()
        
        return jsonify(reservation.to_dict()), 201
        
    except ValueError as e:
        return jsonify({'error': f'Invalid datetime format: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@reservations_bp.route('/reservations/<int:reservation_id>', methods=['PUT'])
@jwt_required()
def update_reservation(reservation_id):
    """Update reservation"""
    user_id = get_jwt_identity()
    user = AppUser.query.get(user_id)
    
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Check permissions
    if not user.is_admin() and reservation.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Check if user can modify (time limit check for non-admins)
    if not user.is_admin() and not reservation.can_be_modified_by_user():
        return jsonify({'error': 'Reservation cannot be modified less than 2 hours before start time'}), 403
    
    data = request.get_json()
    
    try:
        # Update time fields if provided
        if 'start_time' in data or 'end_time' in data:
            start_time = reservation.start_time
            end_time = reservation.end_time
            
            if 'start_time' in data:
                start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
            
            if 'end_time' in data:
                end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
            
            # Validate time range
            if start_time >= end_time:
                return jsonify({'error': 'End time must be after start time'}), 400
            
            if start_time < datetime.utcnow():
                return jsonify({'error': 'Cannot set reservation start time in the past'}), 400
            
            # Check availability (excluding current reservation)
            vehicle = Vehicle.query.get(reservation.vehicle_id)
            if not vehicle.is_available(start_time, end_time, exclude_reservation_id=reservation_id):
                return jsonify({'error': 'Vehicle is not available for the selected time period'}), 400
            
            reservation.start_time = start_time
            reservation.end_time = end_time
        
        # Update other fields
        updatable_fields = ['purpose', 'destination', 'number_of_passengers', 'user_notes']
        for field in updatable_fields:
            if field in data:
                setattr(reservation, field, data[field])
        
        # Admin can update admin_notes and status
        if user.is_admin():
            if 'admin_notes' in data:
                reservation.admin_notes = data['admin_notes']
            if 'status' in data:
                reservation.status = data['status']
        
        db.session.commit()
        return jsonify(reservation.to_dict()), 200
        
    except ValueError as e:
        return jsonify({'error': f'Invalid datetime format: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@reservations_bp.route('/reservations/<int:reservation_id>', methods=['DELETE'])
@jwt_required()
def cancel_reservation(reservation_id):
    """Cancel reservation"""
    user_id = get_jwt_identity()
    user = AppUser.query.get(user_id)
    
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Check permissions
    if not user.is_admin() and reservation.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Check if user can cancel (time limit check for non-admins)
    if not user.is_admin() and not reservation.can_be_modified_by_user():
        return jsonify({'error': 'Reservation cannot be cancelled less than 2 hours before start time'}), 403
    
    # Update status instead of deleting
    reservation.status = 'Cancelled'
    db.session.commit()
    
    return jsonify({'message': 'Reservation cancelled successfully'}), 200

@reservations_bp.route('/calendar', methods=['GET'])
@jwt_required()
def get_calendar_data():
    """Get calendar data for all vehicles"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    vehicle_id = request.args.get('vehicle_id')
    
    if not start_date or not end_date:
        return jsonify({'error': 'start_date and end_date parameters are required'}), 400
    
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    query = Reservation.query.filter(
        Reservation.status == 'Confirmed',
        Reservation.start_time <= end_dt,
        Reservation.end_time >= start_dt
    )
    
    if vehicle_id:
        query = query.filter_by(vehicle_id=int(vehicle_id))
    
    reservations = query.all()
    
    # Format for calendar display
    calendar_events = []
    for reservation in reservations:
        calendar_events.append({
            'id': reservation.reservation_id,
            'title': f'{reservation.vehicle.license_plate} - {reservation.user.first_name} {reservation.user.last_name}',
            'start': reservation.start_time.isoformat(),
            'end': reservation.end_time.isoformat(),
            'vehicle_id': reservation.vehicle_id,
            'user_id': reservation.user_id,
            'purpose': reservation.purpose,
            'destination': reservation.destination
        })
    
    return jsonify(calendar_events), 200

