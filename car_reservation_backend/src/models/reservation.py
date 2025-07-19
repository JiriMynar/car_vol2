from src.models.database import db, BaseModel
from datetime import datetime

class Reservation(BaseModel):
    __tablename__ = 'reservations'
    
    reservation_id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.vehicle_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    purpose = db.Column(db.String(255), nullable=False)
    destination = db.Column(db.String(255), nullable=False)
    number_of_passengers = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(50), nullable=False, default='Confirmed')
    user_notes = db.Column(db.Text, nullable=True)
    admin_notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Reservation {self.reservation_id}: {self.vehicle.license_plate if self.vehicle else "N/A"} ({self.start_time} - {self.end_time})>'
    
    def to_dict(self):
        return {
            'reservation_id': self.reservation_id,
            'vehicle_id': self.vehicle_id,
            'vehicle_info': {
                'make': self.vehicle.make,
                'model': self.vehicle.model,
                'license_plate': self.vehicle.license_plate
            } if self.vehicle else None,
            'user_id': self.user_id,
            'user_info': {
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'email': self.user.email
            } if self.user else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'purpose': self.purpose,
            'destination': self.destination,
            'number_of_passengers': self.number_of_passengers,
            'status': self.status,
            'user_notes': self.user_notes,
            'admin_notes': self.admin_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def is_active(self):
        """Kontrola, zda je rezervace aktuálně aktivní (potvrzená a neprošlá)"""
        return self.status == 'Confirmed' and self.end_time > datetime.utcnow()
    
    def can_be_modified_by_user(self, hours_before=2):
        """Kontrola, zda může být rezervace upravena uživatelem (konfigurovatelné hodiny před začátkem)"""
        if self.status != 'Confirmed':
            return False
        
        time_until_start = (self.start_time - datetime.utcnow()).total_seconds() / 3600
        return time_until_start >= hours_before

